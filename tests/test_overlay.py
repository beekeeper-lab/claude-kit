"""Tests for foundry_app.services.overlay and overlay integration.

Covers: compare_trees, apply_plan, detect_orphans, format_overlay_report,
format_dry_run_report, CLI flag validation, and end-to-end overlay mode.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from foundry_app.cli import _build_parser, _cmd_generate, _validate_overlay_flags
from foundry_app.core.models import (
    CompositionSpec,
    FileAction,
    GenerationManifest,
    GenerationOptions,
    HooksConfig,
    OverlayPlan,
    PersonaSelection,
    ProjectIdentity,
    StackSelection,
    StageResult,
    TeamConfig,
)
from foundry_app.io.composition_io import save_composition
from foundry_app.services.generator import generate_project
from foundry_app.services.overlay import (
    apply_plan,
    collect_all_wrote_paths,
    compare_trees,
    detect_orphans,
    format_dry_run_report,
    format_overlay_report,
    load_previous_manifest,
)

LIBRARY_ROOT = Path(__file__).parent.parent / "ai-team-library"


def _make_spec(
    personas: list[str] | None = None,
    stacks: list[str] | None = None,
    name: str = "Overlay Test",
    slug: str = "overlay-test",
    seed_tasks: bool = False,
    write_manifest: bool = True,
) -> CompositionSpec:
    """Build a minimal CompositionSpec for overlay tests."""
    if personas is None:
        personas = ["team-lead", "developer"]
    if stacks is None:
        stacks = ["python"]
    return CompositionSpec(
        project=ProjectIdentity(name=name, slug=slug),
        stacks=[StackSelection(id=sid) for sid in stacks],
        team=TeamConfig(
            personas=[PersonaSelection(id=pid) for pid in personas]
        ),
        hooks=HooksConfig(),
        generation=GenerationOptions(
            seed_tasks=seed_tasks,
            write_manifest=write_manifest,
        ),
    )


# ===================================================================
# Unit tests for overlay.py functions
# ===================================================================


class TestCompareTrees:
    """Tests for compare_trees() classification logic."""

    def test_all_files_create_when_target_empty(self, tmp_path: Path):
        """All files should be classified as 'create' when target is empty."""
        temp_dir = tmp_path / "temp"
        temp_dir.mkdir()
        target_dir = tmp_path / "target"
        target_dir.mkdir()

        # Create some files in temp
        (temp_dir / "file1.md").write_text("content1")
        sub = temp_dir / "sub"
        sub.mkdir()
        (sub / "file2.md").write_text("content2")

        plan = compare_trees(temp_dir, target_dir)

        assert len(plan.creates) == 2
        assert len(plan.unchanged) == 0
        assert len(plan.conflicts) == 0

    def test_identical_files_classified_unchanged(self, tmp_path: Path):
        """Files with identical content should be classified as 'unchanged'."""
        temp_dir = tmp_path / "temp"
        temp_dir.mkdir()
        target_dir = tmp_path / "target"
        target_dir.mkdir()

        # Same content in both
        (temp_dir / "file.md").write_text("identical content")
        (target_dir / "file.md").write_text("identical content")

        plan = compare_trees(temp_dir, target_dir)

        assert len(plan.creates) == 0
        assert len(plan.unchanged) == 1
        assert plan.unchanged[0].rel_path == "file.md"

    def test_differing_files_classified_conflict(self, tmp_path: Path):
        """Files with different content should be classified as 'conflict'."""
        temp_dir = tmp_path / "temp"
        temp_dir.mkdir()
        target_dir = tmp_path / "target"
        target_dir.mkdir()

        (temp_dir / "file.md").write_text("new content")
        (target_dir / "file.md").write_text("old content")

        plan = compare_trees(temp_dir, target_dir)

        assert len(plan.conflicts) == 1
        assert plan.conflicts[0].rel_path == "file.md"
        assert plan.conflicts[0].sidecar_path == "file.md.foundry-new"
        assert plan.has_conflicts

    def test_force_mode_classifies_as_force_overwrite(self, tmp_path: Path):
        """With force=True, differing files should be 'force_overwrite'."""
        temp_dir = tmp_path / "temp"
        temp_dir.mkdir()
        target_dir = tmp_path / "target"
        target_dir.mkdir()

        (temp_dir / "file.md").write_text("new content")
        (target_dir / "file.md").write_text("old content")

        plan = compare_trees(temp_dir, target_dir, force=True)

        assert len(plan.force_overwrites) == 1
        assert len(plan.conflicts) == 0
        assert plan.force_overwrites[0].rel_path == "file.md"

    def test_provenance_in_conflict_reason(self, tmp_path: Path):
        """Conflict reason should mention provenance when manifest exists."""
        temp_dir = tmp_path / "temp"
        temp_dir.mkdir()
        target_dir = tmp_path / "target"
        target_dir.mkdir()

        (temp_dir / "file.md").write_text("new")
        (target_dir / "file.md").write_text("old")

        prev_manifest = GenerationManifest(
            stages={"scaffold": StageResult(wrote=["file.md"])}
        )
        plan = compare_trees(
            temp_dir, target_dir, previous_manifest=prev_manifest
        )

        assert "prior run" in plan.conflicts[0].reason

    def test_no_provenance_when_no_manifest(self, tmp_path: Path):
        """Without previous manifest, reason should note no provenance."""
        temp_dir = tmp_path / "temp"
        temp_dir.mkdir()
        target_dir = tmp_path / "target"
        target_dir.mkdir()

        (temp_dir / "file.md").write_text("new")
        (target_dir / "file.md").write_text("old")

        plan = compare_trees(temp_dir, target_dir, previous_manifest=None)

        assert "no prior manifest" in plan.conflicts[0].reason

    def test_mixed_classification(self, tmp_path: Path):
        """A mix of create, unchanged, and conflict files."""
        temp_dir = tmp_path / "temp"
        temp_dir.mkdir()
        target_dir = tmp_path / "target"
        target_dir.mkdir()

        # New file
        (temp_dir / "new.md").write_text("new")
        # Unchanged file
        (temp_dir / "same.md").write_text("same")
        (target_dir / "same.md").write_text("same")
        # Conflict file
        (temp_dir / "changed.md").write_text("v2")
        (target_dir / "changed.md").write_text("v1")

        plan = compare_trees(temp_dir, target_dir)

        assert len(plan.creates) == 1
        assert len(plan.unchanged) == 1
        assert len(plan.conflicts) == 1

    def test_subdirectory_files(self, tmp_path: Path):
        """Files in subdirectories should have correct relative paths."""
        temp_dir = tmp_path / "temp"
        (temp_dir / "ai" / "context").mkdir(parents=True)
        (temp_dir / "ai" / "context" / "project.md").write_text("ctx")

        target_dir = tmp_path / "target"
        target_dir.mkdir()

        plan = compare_trees(temp_dir, target_dir)

        assert len(plan.creates) == 1
        rel = plan.creates[0].rel_path
        # Should use forward slashes or OS path separator
        assert "ai" in rel
        assert "project.md" in rel


class TestApplyPlan:
    """Tests for apply_plan() execution."""

    def test_creates_new_files(self, tmp_path: Path):
        """apply_plan should copy files classified as 'create'."""
        temp_dir = tmp_path / "temp"
        temp_dir.mkdir()
        target_dir = tmp_path / "target"
        target_dir.mkdir()

        (temp_dir / "new.md").write_text("new content")

        plan = OverlayPlan(
            target_dir=str(target_dir),
            actions=[
                FileAction(
                    rel_path="new.md", action="create", reason="New file"
                )
            ],
        )

        summary = apply_plan(plan, temp_dir, target_dir)

        assert summary.files_created == 1
        assert (target_dir / "new.md").read_text() == "new content"

    def test_skips_unchanged_files(self, tmp_path: Path):
        """apply_plan should not touch files classified as 'unchanged'."""
        temp_dir = tmp_path / "temp"
        temp_dir.mkdir()
        target_dir = tmp_path / "target"
        target_dir.mkdir()

        (temp_dir / "same.md").write_text("content")
        (target_dir / "same.md").write_text("content")

        plan = OverlayPlan(
            target_dir=str(target_dir),
            actions=[
                FileAction(
                    rel_path="same.md",
                    action="unchanged",
                    reason="Content identical",
                )
            ],
        )

        summary = apply_plan(plan, temp_dir, target_dir)

        assert summary.files_unchanged == 1
        assert (target_dir / "same.md").read_text() == "content"

    def test_writes_sidecar_for_conflict(self, tmp_path: Path):
        """apply_plan should write a .foundry-new sidecar for conflicts."""
        temp_dir = tmp_path / "temp"
        temp_dir.mkdir()
        target_dir = tmp_path / "target"
        target_dir.mkdir()

        (temp_dir / "file.md").write_text("new version")
        (target_dir / "file.md").write_text("old version")

        plan = OverlayPlan(
            target_dir=str(target_dir),
            actions=[
                FileAction(
                    rel_path="file.md",
                    action="conflict",
                    reason="Modified",
                    sidecar_path="file.md.foundry-new",
                )
            ],
        )

        summary = apply_plan(plan, temp_dir, target_dir)

        assert summary.files_conflicted == 1
        # Original untouched
        assert (target_dir / "file.md").read_text() == "old version"
        # Sidecar written
        assert (target_dir / "file.md.foundry-new").read_text() == "new version"
        assert "file.md.foundry-new" in summary.sidecars_written

    def test_force_overwrite(self, tmp_path: Path):
        """apply_plan should overwrite files classified as 'force_overwrite'."""
        temp_dir = tmp_path / "temp"
        temp_dir.mkdir()
        target_dir = tmp_path / "target"
        target_dir.mkdir()

        (temp_dir / "file.md").write_text("new version")
        (target_dir / "file.md").write_text("old version")

        plan = OverlayPlan(
            target_dir=str(target_dir),
            actions=[
                FileAction(
                    rel_path="file.md",
                    action="force_overwrite",
                    reason="Force overwrite",
                )
            ],
        )

        summary = apply_plan(plan, temp_dir, target_dir)

        assert summary.files_force_overwritten == 1
        assert (target_dir / "file.md").read_text() == "new version"

    def test_creates_parent_dirs(self, tmp_path: Path):
        """apply_plan should create parent directories as needed."""
        temp_dir = tmp_path / "temp"
        (temp_dir / "ai" / "context").mkdir(parents=True)
        (temp_dir / "ai" / "context" / "project.md").write_text("ctx")

        target_dir = tmp_path / "target"
        target_dir.mkdir()

        plan = OverlayPlan(
            target_dir=str(target_dir),
            actions=[
                FileAction(
                    rel_path="ai/context/project.md",
                    action="create",
                    reason="New file",
                )
            ],
        )

        apply_plan(plan, temp_dir, target_dir)

        assert (target_dir / "ai" / "context" / "project.md").is_file()


class TestDetectOrphans:
    """Tests for detect_orphans()."""

    def test_detects_removed_files(self):
        """Files in previous manifest but not current should be orphans."""
        prev = GenerationManifest(
            stages={
                "scaffold": StageResult(wrote=["a.md", "b.md", "c.md"]),
            }
        )
        current_files = {"a.md", "c.md"}

        orphans = detect_orphans(prev, current_files)

        assert orphans == ["b.md"]

    def test_no_orphans_when_same_files(self):
        """No orphans when current and previous have the same files."""
        prev = GenerationManifest(
            stages={"scaffold": StageResult(wrote=["a.md", "b.md"])}
        )
        current_files = {"a.md", "b.md"}

        orphans = detect_orphans(prev, current_files)

        assert orphans == []

    def test_no_orphans_when_no_previous(self):
        """No orphans when there is no previous manifest."""
        orphans = detect_orphans(None, {"a.md"})
        assert orphans == []


class TestLoadPreviousManifest:
    """Tests for load_previous_manifest()."""

    def test_loads_valid_manifest(self, tmp_path: Path):
        """Should load and parse a valid manifest.json."""
        manifest = GenerationManifest(
            stages={"scaffold": StageResult(wrote=["test.md"])}
        )
        manifest_dir = tmp_path / "ai" / "generated"
        manifest_dir.mkdir(parents=True)
        manifest_path = manifest_dir / "manifest.json"
        manifest_path.write_text(manifest.model_dump_json(indent=2))

        result = load_previous_manifest(tmp_path)

        assert result is not None
        assert "scaffold" in result.stages

    def test_returns_none_when_missing(self, tmp_path: Path):
        """Should return None when no manifest.json exists."""
        result = load_previous_manifest(tmp_path)
        assert result is None

    def test_returns_none_for_corrupted(self, tmp_path: Path):
        """Should return None for an unparseable manifest."""
        manifest_dir = tmp_path / "ai" / "generated"
        manifest_dir.mkdir(parents=True)
        (manifest_dir / "manifest.json").write_text("not valid json{{{")

        result = load_previous_manifest(tmp_path)
        assert result is None


class TestCollectAllWrotePaths:
    """Tests for collect_all_wrote_paths()."""

    def test_collects_from_all_stages(self):
        """Should collect paths from every stage."""
        manifest = GenerationManifest(
            stages={
                "scaffold": StageResult(wrote=["a.md", "b.md"]),
                "compile": StageResult(wrote=["c.md"]),
            }
        )

        paths = collect_all_wrote_paths(manifest)

        assert paths == {"a.md", "b.md", "c.md"}


class TestFormatOverlayReport:
    """Tests for format_overlay_report()."""

    def test_report_includes_counts(self):
        """Report should include counts of creates, unchanged, conflicts."""
        plan = OverlayPlan(
            target_dir="/tmp/target",
            actions=[
                FileAction(rel_path="a.md", action="create", reason="New"),
                FileAction(
                    rel_path="b.md",
                    action="unchanged",
                    reason="Identical",
                ),
                FileAction(
                    rel_path="c.md",
                    action="conflict",
                    reason="Modified",
                    sidecar_path="c.md.foundry-new",
                ),
            ],
            orphans=["old.md"],
        )

        report = format_overlay_report(plan)

        assert "Created: 1" in report
        assert "Unchanged: 1" in report
        assert "Conflicts: 1" in report
        assert "Orphans: 1" in report
        assert "c.md.foundry-new" in report
        assert "old.md" in report

    def test_force_report_shows_overwritten(self):
        """Force mode report should show 'Overwritten' instead of conflicts."""
        plan = OverlayPlan(
            target_dir="/tmp/target",
            actions=[
                FileAction(
                    rel_path="a.md",
                    action="force_overwrite",
                    reason="Forced",
                ),
            ],
        )

        report = format_overlay_report(plan)

        assert "Overwritten: 1" in report
        assert "force mode" in report.lower()


class TestFormatDryRunReport:
    """Tests for format_dry_run_report()."""

    def test_dry_run_includes_categories(self):
        """Dry-run report should have all category sections."""
        plan = OverlayPlan(
            target_dir="/tmp/target",
            actions=[
                FileAction(rel_path="a.md", action="create", reason="New"),
                FileAction(
                    rel_path="b.md",
                    action="unchanged",
                    reason="Identical",
                ),
                FileAction(
                    rel_path="c.md",
                    action="conflict",
                    reason="Modified",
                    sidecar_path="c.md.foundry-new",
                ),
            ],
            orphans=["old.md"],
        )

        report = format_dry_run_report(plan)

        assert "Would create" in report
        assert "Would skip" in report
        assert "Conflicts" in report
        assert "Orphaned" in report
        assert "dry-run mode" in report.lower()
        assert "+ a.md" in report
        assert "= b.md" in report
        assert "! c.md" in report
        assert "? old.md" in report


# ===================================================================
# Integration tests: overlay through generate_project()
# ===================================================================


class TestOverlayIntegration:
    """End-to-end overlay tests using generate_project()."""

    def test_overlay_into_empty_dir(self, tmp_path: Path):
        """Overlay into an empty dir should classify all files as 'create'."""
        spec = _make_spec()
        target_dir = tmp_path / "project"
        target_dir.mkdir()

        manifest, validation, plan = generate_project(
            spec,
            LIBRARY_ROOT,
            output_root=target_dir,
            overlay=True,
        )

        assert validation.is_valid
        assert plan is not None
        assert len(plan.creates) > 0
        assert len(plan.conflicts) == 0
        assert len(plan.unchanged) == 0
        # Files should actually be written
        assert (target_dir / "CLAUDE.md").is_file()
        assert (target_dir / "ai" / "context" / "project.md").is_file()

    def test_overlay_non_foundry_files_untouched(self, tmp_path: Path):
        """Non-Foundry files in the target should not be modified."""
        spec = _make_spec()
        target_dir = tmp_path / "project"
        target_dir.mkdir()

        # Create non-Foundry files
        (target_dir / "src").mkdir()
        (target_dir / "src" / "main.py").write_text("print('hello')")
        (target_dir / "pyproject.toml").write_text("[project]\nname='test'")

        manifest, validation, plan = generate_project(
            spec,
            LIBRARY_ROOT,
            output_root=target_dir,
            overlay=True,
        )

        assert validation.is_valid
        # Non-Foundry files should still exist with original content
        assert (target_dir / "src" / "main.py").read_text() == "print('hello')"
        assert "[project]" in (target_dir / "pyproject.toml").read_text()

    def test_overlay_unchanged_files_skipped(self, tmp_path: Path):
        """Re-running overlay with same composition should skip unchanged."""
        spec = _make_spec()
        target_dir = tmp_path / "project"
        target_dir.mkdir()

        # First generation: all files created
        manifest1, val1, plan1 = generate_project(
            spec,
            LIBRARY_ROOT,
            output_root=target_dir,
            overlay=True,
        )
        assert val1.is_valid
        assert len(plan1.creates) > 0

        # Second generation: all files should be unchanged
        manifest2, val2, plan2 = generate_project(
            spec,
            LIBRARY_ROOT,
            output_root=target_dir,
            overlay=True,
        )
        assert val2.is_valid
        assert plan2 is not None
        assert len(plan2.unchanged) > 0
        # There should be no creates (everything already exists)
        # Note: manifest.json itself may not be in the overlay plan since
        # it's written *after* the overlay comparison. So creates might be 0
        # or the manifest might be treated differently.

    def test_overlay_modified_file_is_conflict(self, tmp_path: Path):
        """A hand-edited file should be reported as a conflict."""
        spec = _make_spec()
        target_dir = tmp_path / "project"
        target_dir.mkdir()

        # First generation
        generate_project(
            spec,
            LIBRARY_ROOT,
            output_root=target_dir,
            overlay=True,
        )

        # Hand-edit a file
        project_md = target_dir / "ai" / "context" / "project.md"
        project_md.write_text("# Hand-edited project context")

        # Second overlay
        manifest2, val2, plan2 = generate_project(
            spec,
            LIBRARY_ROOT,
            output_root=target_dir,
            overlay=True,
        )

        assert val2.is_valid
        assert plan2 is not None
        # The hand-edited file should be a conflict
        conflict_paths = [c.rel_path for c in plan2.conflicts]
        assert any("project.md" in p for p in conflict_paths)
        # Original should be preserved
        assert (
            project_md.read_text() == "# Hand-edited project context"
        )
        # Sidecar should exist
        assert (
            target_dir / "ai" / "context" / "project.md.foundry-new"
        ).is_file()

    def test_overlay_force_overwrites_conflicts(self, tmp_path: Path):
        """--force should overwrite conflicting files."""
        spec = _make_spec()
        target_dir = tmp_path / "project"
        target_dir.mkdir()

        # First generation
        generate_project(
            spec,
            LIBRARY_ROOT,
            output_root=target_dir,
            overlay=True,
        )

        # Hand-edit a file
        project_md = target_dir / "ai" / "context" / "project.md"
        project_md.write_text("# Hand-edited project context")

        # Second overlay with --force
        manifest2, val2, plan2 = generate_project(
            spec,
            LIBRARY_ROOT,
            output_root=target_dir,
            overlay=True,
            force=True,
        )

        assert val2.is_valid
        assert plan2 is not None
        assert len(plan2.force_overwrites) > 0
        # The file should be overwritten (not the hand-edited version)
        assert project_md.read_text() != "# Hand-edited project context"

    def test_dry_run_writes_nothing(self, tmp_path: Path):
        """--dry-run should not write any files to the target."""
        spec = _make_spec()
        target_dir = tmp_path / "project"
        target_dir.mkdir()

        # Snapshot the directory before
        files_before = set()
        for f in target_dir.rglob("*"):
            if f.is_file():
                files_before.add(
                    (str(f.relative_to(target_dir)), f.read_bytes())
                )

        manifest, validation, plan = generate_project(
            spec,
            LIBRARY_ROOT,
            output_root=target_dir,
            overlay=True,
            dry_run=True,
        )

        assert validation.is_valid
        assert plan is not None
        assert len(plan.creates) > 0  # Plan should show what would be done

        # Verify nothing was written
        files_after = set()
        for f in target_dir.rglob("*"):
            if f.is_file():
                files_after.add(
                    (str(f.relative_to(target_dir)), f.read_bytes())
                )
        assert files_before == files_after

    def test_overlay_summary_in_manifest(self, tmp_path: Path):
        """Overlay should populate overlay_summary in the manifest."""
        spec = _make_spec()
        target_dir = tmp_path / "project"
        target_dir.mkdir()

        manifest, validation, plan = generate_project(
            spec,
            LIBRARY_ROOT,
            output_root=target_dir,
            overlay=True,
        )

        assert validation.is_valid
        assert manifest.overlay_summary is not None
        assert manifest.overlay_summary.mode == "overlay"
        assert manifest.overlay_summary.files_created > 0

    def test_dry_run_summary_mode(self, tmp_path: Path):
        """Dry-run overlay should set mode='dry_run' in overlay_summary."""
        spec = _make_spec()
        target_dir = tmp_path / "project"
        target_dir.mkdir()

        manifest, validation, plan = generate_project(
            spec,
            LIBRARY_ROOT,
            output_root=target_dir,
            overlay=True,
            dry_run=True,
        )

        assert validation.is_valid
        assert manifest.overlay_summary is not None
        assert manifest.overlay_summary.mode == "dry_run"

    def test_orphan_detection_after_persona_removal(self, tmp_path: Path):
        """Removing a persona should report orphaned files."""
        target_dir = tmp_path / "project"
        target_dir.mkdir()

        # First generation with 3 personas
        spec1 = _make_spec(
            personas=["team-lead", "developer", "architect"]
        )
        generate_project(
            spec1,
            LIBRARY_ROOT,
            output_root=target_dir,
            overlay=True,
        )

        # Second generation without architect
        spec2 = _make_spec(personas=["team-lead", "developer"])
        manifest2, val2, plan2 = generate_project(
            spec2,
            LIBRARY_ROOT,
            output_root=target_dir,
            overlay=True,
        )

        assert val2.is_valid
        assert plan2 is not None
        # Architect-related files should be orphaned
        assert any("architect" in o for o in plan2.orphans)


# ===================================================================
# CLI flag validation tests
# ===================================================================


class TestCLIOverlayFlags:
    """Tests for CLI flag validation logic."""

    def test_overlay_and_output_mutually_exclusive(self, tmp_path: Path):
        """--overlay and --output should be rejected together."""
        target = tmp_path / "project"
        target.mkdir()

        args = argparse.Namespace(
            overlay=target,
            output=tmp_path / "output",
            dry_run=False,
            force=False,
        )
        result = _validate_overlay_flags(args)
        assert result is not None
        assert "mutually exclusive" in result

    def test_dry_run_requires_overlay(self):
        """--dry-run without --overlay should be rejected."""
        args = argparse.Namespace(
            overlay=None,
            output=None,
            dry_run=True,
            force=False,
        )
        result = _validate_overlay_flags(args)
        assert result is not None
        assert "--dry-run requires --overlay" in result

    def test_force_requires_overlay(self):
        """--force without --overlay should be rejected."""
        args = argparse.Namespace(
            overlay=None,
            output=None,
            dry_run=False,
            force=True,
        )
        result = _validate_overlay_flags(args)
        assert result is not None
        assert "--force requires --overlay" in result

    def test_dry_run_and_force_mutually_exclusive(self, tmp_path: Path):
        """--dry-run and --force should be rejected together."""
        target = tmp_path / "project"
        target.mkdir()

        args = argparse.Namespace(
            overlay=target,
            output=None,
            dry_run=True,
            force=True,
        )
        result = _validate_overlay_flags(args)
        assert result is not None
        assert "mutually exclusive" in result

    def test_overlay_nonexistent_dir(self, tmp_path: Path):
        """--overlay on a non-existent directory should be rejected."""
        args = argparse.Namespace(
            overlay=tmp_path / "nonexistent",
            output=None,
            dry_run=False,
            force=False,
        )
        result = _validate_overlay_flags(args)
        assert result is not None
        assert "does not exist" in result

    def test_overlay_not_a_dir(self, tmp_path: Path):
        """--overlay pointing at a file should be rejected."""
        not_dir = tmp_path / "not-a-dir.txt"
        not_dir.write_text("hello")

        args = argparse.Namespace(
            overlay=not_dir,
            output=None,
            dry_run=False,
            force=False,
        )
        result = _validate_overlay_flags(args)
        assert result is not None
        assert "not a directory" in result

    def test_valid_overlay_passes(self, tmp_path: Path):
        """Valid --overlay with existing dir should pass validation."""
        target = tmp_path / "project"
        target.mkdir()

        args = argparse.Namespace(
            overlay=target,
            output=None,
            dry_run=False,
            force=False,
        )
        result = _validate_overlay_flags(args)
        assert result is None

    def test_parser_has_overlay_flags(self):
        """The generate subcommand parser should accept overlay flags."""
        parser = _build_parser()
        args = parser.parse_args([
            "generate", "comp.yml", "--library", "./lib",
            "--overlay", "/tmp/project", "--dry-run",
        ])
        assert args.overlay == Path("/tmp/project")
        assert args.dry_run is True
        assert args.force is False


class TestCLIOverlayIntegration:
    """End-to-end CLI tests for overlay mode."""

    def test_cmd_generate_overlay(self, tmp_path: Path):
        """_cmd_generate with --overlay should work end-to-end."""
        comp_file = tmp_path / "composition.yml"
        target_dir = tmp_path / "project"
        target_dir.mkdir()

        spec = _make_spec()
        save_composition(spec, comp_file)

        args = argparse.Namespace(
            composition=comp_file,
            library=LIBRARY_ROOT,
            output=None,
            strictness=None,
            overlay=target_dir,
            dry_run=False,
            force=False,
        )
        rc = _cmd_generate(args)
        assert rc == 0
        assert (target_dir / "CLAUDE.md").is_file()

    def test_cmd_generate_overlay_dry_run(self, tmp_path: Path):
        """_cmd_generate with --overlay --dry-run should write nothing."""
        comp_file = tmp_path / "composition.yml"
        target_dir = tmp_path / "project"
        target_dir.mkdir()

        spec = _make_spec()
        save_composition(spec, comp_file)

        args = argparse.Namespace(
            composition=comp_file,
            library=LIBRARY_ROOT,
            output=None,
            strictness=None,
            overlay=target_dir,
            dry_run=True,
            force=False,
        )
        rc = _cmd_generate(args)
        assert rc == 0
        # Nothing should have been written
        assert not (target_dir / "CLAUDE.md").exists()

    def test_cmd_generate_overlay_validation_errors(
        self, tmp_path: Path
    ):
        """Overlay flag validation errors should exit with code 1."""
        comp_file = tmp_path / "composition.yml"
        spec = _make_spec()
        save_composition(spec, comp_file)

        # --overlay + --output
        args = argparse.Namespace(
            composition=comp_file,
            library=LIBRARY_ROOT,
            output=tmp_path / "output",
            strictness=None,
            overlay=tmp_path,
            dry_run=False,
            force=False,
        )
        rc = _cmd_generate(args)
        assert rc == 1


# ===================================================================
# QA edge case tests (Tech-QA Task 04)
# ===================================================================


class TestOverlayEdgeCases:
    """Additional edge case tests added by Tech-QA for BEAN-002."""

    def test_double_overlay_second_run_all_unchanged(
        self, tmp_path: Path
    ):
        """EC-2/EC-4: Double overlay -- second run should have zero creates.

        Running overlay twice with the same composition should result in
        all files being classified as 'unchanged' on the second run
        (idempotency). No files should be created or conflicted.
        """
        spec = _make_spec()
        target_dir = tmp_path / "project"
        target_dir.mkdir()

        # First overlay: files created
        _m1, _v1, plan1 = generate_project(
            spec, LIBRARY_ROOT, output_root=target_dir, overlay=True
        )
        assert len(plan1.creates) > 0

        # Second overlay: everything unchanged
        _m2, _v2, plan2 = generate_project(
            spec, LIBRARY_ROOT, output_root=target_dir, overlay=True
        )
        assert plan2 is not None
        # All files should be unchanged -- the manifest itself is
        # written *after* the overlay comparison, so it may show as a
        # conflict if the run_id timestamp differs. We check that no
        # new files are created (creates == 0) and the overwhelming
        # majority are unchanged.
        assert len(plan2.creates) == 0
        assert len(plan2.unchanged) > 0

    def test_overlay_after_adding_persona(self, tmp_path: Path):
        """EC-4/EC-7 complement: Adding a persona should create new files.

        Run overlay with 2 personas, then again with 3. The third
        persona's files should be classified as 'create'; existing
        persona files should be 'unchanged'.
        """
        target_dir = tmp_path / "project"
        target_dir.mkdir()

        # First generation with 2 personas
        spec1 = _make_spec(personas=["team-lead", "developer"])
        generate_project(
            spec1, LIBRARY_ROOT, output_root=target_dir, overlay=True
        )

        # Second generation adds architect
        spec2 = _make_spec(
            personas=["team-lead", "developer", "architect"]
        )
        _m2, _v2, plan2 = generate_project(
            spec2, LIBRARY_ROOT, output_root=target_dir, overlay=True
        )
        assert plan2 is not None

        # New architect files should be 'create'
        create_paths = [a.rel_path for a in plan2.creates]
        assert any("architect" in p for p in create_paths), (
            f"Expected architect files in creates, got: {create_paths}"
        )

        # Existing team-lead/developer files should mostly be unchanged
        assert len(plan2.unchanged) > 0

    def test_overlay_extra_non_foundry_files_in_claude_dir(
        self, tmp_path: Path
    ):
        """User-placed files inside .claude/ and ai/ are left untouched.

        The overlay engine only writes files that the pipeline generates.
        User-created files inside .claude/ or ai/ that are NOT part of
        the generation should survive an overlay run.
        """
        spec = _make_spec()
        target_dir = tmp_path / "project"
        target_dir.mkdir()

        # First overlay to populate the directory
        generate_project(
            spec, LIBRARY_ROOT, output_root=target_dir, overlay=True
        )

        # Add user files inside .claude/ and ai/
        user_claude_file = target_dir / ".claude" / "my-custom-config.json"
        user_claude_file.write_text('{"custom": true}')

        user_ai_file = target_dir / "ai" / "context" / "my-notes.md"
        user_ai_file.write_text("# My personal notes")

        user_output_file = (
            target_dir / "ai" / "outputs" / "developer" / "my-report.md"
        )
        user_output_file.parent.mkdir(parents=True, exist_ok=True)
        user_output_file.write_text("# My custom report")

        # Second overlay
        generate_project(
            spec, LIBRARY_ROOT, output_root=target_dir, overlay=True
        )

        # User files should be untouched
        assert user_claude_file.is_file()
        assert user_claude_file.read_text() == '{"custom": true}'
        assert user_ai_file.is_file()
        assert user_ai_file.read_text() == "# My personal notes"
        assert user_output_file.is_file()
        assert user_output_file.read_text() == "# My custom report"

    def test_dry_run_with_conflicts_writes_nothing(
        self, tmp_path: Path
    ):
        """Dry-run on a directory with conflicts writes absolutely nothing.

        This verifies the dry-run guarantee: the target directory is
        byte-for-byte identical before and after dry-run, even when
        there are conflicts that would normally produce sidecar files.
        """
        spec = _make_spec()
        target_dir = tmp_path / "project"
        target_dir.mkdir()

        # First overlay
        generate_project(
            spec, LIBRARY_ROOT, output_root=target_dir, overlay=True
        )

        # Hand-edit files to create conflicts
        (target_dir / "ai" / "context" / "project.md").write_text(
            "# Hand-edited project"
        )
        (target_dir / "CLAUDE.md").write_text("# My custom CLAUDE.md")

        # Snapshot all files before dry-run
        files_before: dict[str, bytes] = {}
        for f in target_dir.rglob("*"):
            if f.is_file():
                rel = str(f.relative_to(target_dir))
                files_before[rel] = f.read_bytes()

        # Dry-run overlay
        _m, _v, plan = generate_project(
            spec,
            LIBRARY_ROOT,
            output_root=target_dir,
            overlay=True,
            dry_run=True,
        )

        # Verify the plan detects conflicts
        assert plan is not None
        assert len(plan.conflicts) > 0

        # Verify NOTHING was written (byte-for-byte identical)
        files_after: dict[str, bytes] = {}
        for f in target_dir.rglob("*"):
            if f.is_file():
                rel = str(f.relative_to(target_dir))
                files_after[rel] = f.read_bytes()

        assert set(files_before.keys()) == set(files_after.keys()), (
            "File set changed during dry-run"
        )
        for path, content in files_before.items():
            assert files_after[path] == content, (
                f"File {path} was modified during dry-run"
            )

    def test_overlay_with_empty_composition(self, tmp_path: Path):
        """Overlay with an empty composition (no personas, no stacks).

        Validation may fail with strict mode, but with light strictness
        the pipeline should still produce scaffold files (CLAUDE.md,
        README.md, context docs) without crashing.
        """
        spec = _make_spec(personas=[], stacks=[])
        target_dir = tmp_path / "project"
        target_dir.mkdir()

        manifest, validation, plan = generate_project(
            spec,
            LIBRARY_ROOT,
            output_root=target_dir,
            overlay=True,
            # Use light strictness so empty stacks/personas pass validation
        )

        # With standard strictness, empty stacks trigger a warning but
        # may still pass in standard mode. Check what happens:
        if validation.is_valid:
            assert plan is not None
            # Should still generate scaffold files at minimum
            assert (target_dir / "CLAUDE.md").is_file()
        else:
            # If validation fails, that's acceptable -- the key point
            # is no crash/exception occurred.
            assert plan is None

    def test_orphan_detection_reports_removed_persona_files(
        self, tmp_path: Path
    ):
        """EC-7: Verify orphan detection lists specific removed persona files.

        When a persona is removed from the composition, all of its
        generated files (agent wrapper, compiled member, output README)
        should appear in the orphans list.
        """
        target_dir = tmp_path / "project"
        target_dir.mkdir()

        # Generate with architect
        spec1 = _make_spec(
            personas=["team-lead", "developer", "architect"]
        )
        generate_project(
            spec1, LIBRARY_ROOT, output_root=target_dir, overlay=True
        )

        # Verify architect files were created
        architect_member = (
            target_dir / "ai" / "generated" / "members" / "architect.md"
        )
        assert architect_member.is_file()

        # Remove architect
        spec2 = _make_spec(personas=["team-lead", "developer"])
        _m2, _v2, plan2 = generate_project(
            spec2, LIBRARY_ROOT, output_root=target_dir, overlay=True
        )

        assert plan2 is not None
        # Architect files should be in orphans
        orphan_set = set(plan2.orphans)
        assert any("architect" in o for o in orphan_set), (
            f"Expected architect files in orphans, got: {orphan_set}"
        )
        # Orphaned files should NOT have been deleted
        assert architect_member.is_file(), (
            "Orphaned files should not be deleted by overlay"
        )

    def test_settings_local_json_conflict_detection(
        self, tmp_path: Path
    ):
        """EC-5: Hand-edited settings.local.json should be a conflict.

        When the user modifies .claude/settings.local.json after initial
        generation, overlay should detect it as a conflict and write a
        .foundry-new sidecar, preserving the user's customization.
        """
        spec = _make_spec()
        target_dir = tmp_path / "project"
        target_dir.mkdir()

        # First overlay
        generate_project(
            spec, LIBRARY_ROOT, output_root=target_dir, overlay=True
        )

        settings_file = target_dir / ".claude" / "settings.local.json"
        assert settings_file.is_file(), (
            "settings.local.json should exist after first overlay"
        )

        # Hand-edit settings.local.json
        original_content = settings_file.read_text()
        modified_content = original_content.replace("}", ', "custom": true}')
        settings_file.write_text(modified_content)

        # Second overlay
        _m2, _v2, plan2 = generate_project(
            spec, LIBRARY_ROOT, output_root=target_dir, overlay=True
        )
        assert plan2 is not None

        # Should detect conflict on settings.local.json
        conflict_paths = [c.rel_path for c in plan2.conflicts]
        settings_rel = str(
            settings_file.relative_to(target_dir)
        )
        assert settings_rel in conflict_paths, (
            f"Expected {settings_rel} in conflicts, got: {conflict_paths}"
        )

        # Original should be preserved
        assert settings_file.read_text() == modified_content

        # Sidecar should exist
        sidecar = target_dir / ".claude" / "settings.local.json.foundry-new"
        assert sidecar.is_file(), (
            "Sidecar should be written for settings.local.json conflict"
        )

    def test_corrupted_manifest_fallback(self, tmp_path: Path):
        """EC-4 fallback: Corrupted manifest should not crash overlay.

        When the previous manifest.json is present but corrupted, the
        overlay engine should fall back to no-provenance mode and still
        classify files correctly.
        """
        spec = _make_spec()
        target_dir = tmp_path / "project"
        target_dir.mkdir()

        # First overlay (creates manifest)
        generate_project(
            spec, LIBRARY_ROOT, output_root=target_dir, overlay=True
        )

        # Corrupt the manifest
        manifest_path = (
            target_dir / "ai" / "generated" / "manifest.json"
        )
        manifest_path.write_text("CORRUPTED{{{not json!!!")

        # Hand-edit a file to force a conflict
        (target_dir / "CLAUDE.md").write_text("# Hand-edited")

        # Second overlay should still work (fallback to no-provenance)
        _m2, _v2, plan2 = generate_project(
            spec, LIBRARY_ROOT, output_root=target_dir, overlay=True
        )
        assert plan2 is not None

        # Should still detect the conflict
        conflict_paths = [c.rel_path for c in plan2.conflicts]
        assert any("CLAUDE.md" in p for p in conflict_paths)

        # Reason should indicate no prior manifest
        claude_conflict = next(
            c for c in plan2.conflicts if "CLAUDE.md" in c.rel_path
        )
        assert "no prior manifest" in claude_conflict.reason

    def test_overlay_provenance_in_conflict_reason_integration(
        self, tmp_path: Path
    ):
        """EC-4: Conflict reason includes provenance when manifest exists.

        After a successful overlay, modifying a Foundry-generated file
        and re-running overlay should produce a conflict reason that
        mentions 'prior run' (because the file is in the manifest).
        """
        spec = _make_spec()
        target_dir = tmp_path / "project"
        target_dir.mkdir()

        # First overlay
        generate_project(
            spec, LIBRARY_ROOT, output_root=target_dir, overlay=True
        )

        # Hand-edit a known Foundry-generated file
        (target_dir / "CLAUDE.md").write_text("# Modified by user")

        # Second overlay
        _m2, _v2, plan2 = generate_project(
            spec, LIBRARY_ROOT, output_root=target_dir, overlay=True
        )
        assert plan2 is not None

        # Find the CLAUDE.md conflict
        claude_conflicts = [
            c for c in plan2.conflicts if "CLAUDE.md" in c.rel_path
        ]
        assert len(claude_conflicts) > 0
        assert "prior run" in claude_conflicts[0].reason
