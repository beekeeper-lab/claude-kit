"""Overlay engine: two-phase generate-then-compare for overlay mode.

Compares a freshly generated temp directory against an existing target
directory, classifies every file, and applies the plan (or reports it
for dry-run mode).
"""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path

from foundry_app.core.models import (
    FileAction,
    GenerationManifest,
    OverlayPlan,
    OverlaySummary,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_previous_manifest(target_dir: Path) -> GenerationManifest | None:
    """Load ai/generated/manifest.json from the target directory.

    Returns None if the manifest is missing or cannot be parsed.
    """
    manifest_path = target_dir / "ai" / "generated" / "manifest.json"
    if not manifest_path.is_file():
        return None
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        return GenerationManifest.model_validate(data)
    except Exception:  # noqa: BLE001
        logger.warning("Could not parse previous manifest at %s", manifest_path)
        return None


def collect_all_wrote_paths(manifest: GenerationManifest) -> set[str]:
    """Collect every file path recorded across all stages in a manifest."""
    paths: set[str] = set()
    for stage_result in manifest.stages.values():
        paths.update(stage_result.wrote)
    return paths


def compare_trees(
    temp_dir: Path,
    target_dir: Path,
    previous_manifest: GenerationManifest | None = None,
    force: bool = False,
) -> OverlayPlan:
    """Walk the temp directory and classify every file against the target.

    Args:
        temp_dir: Directory containing freshly generated files.
        target_dir: Existing project directory (overlay target).
        previous_manifest: Previous generation manifest for provenance info.
        force: If True, classify differing files as force_overwrite instead
            of conflict.

    Returns:
        An OverlayPlan with a FileAction for every generated file.
    """
    prev_files: set[str] = set()
    if previous_manifest is not None:
        prev_files = collect_all_wrote_paths(previous_manifest)

    actions: list[FileAction] = []

    for temp_file in sorted(temp_dir.rglob("*")):
        if not temp_file.is_file():
            continue

        rel = str(temp_file.relative_to(temp_dir))
        target_file = target_dir / rel

        if not target_file.exists():
            actions.append(FileAction(
                rel_path=rel,
                action="create",
                reason="New file",
            ))
        else:
            if _files_identical(temp_file, target_file):
                actions.append(FileAction(
                    rel_path=rel,
                    action="unchanged",
                    reason="Content identical",
                ))
            else:
                if force:
                    actions.append(FileAction(
                        rel_path=rel,
                        action="force_overwrite",
                        reason=_conflict_reason(rel, prev_files, previous_manifest),
                    ))
                else:
                    sidecar = rel + ".foundry-new"
                    actions.append(FileAction(
                        rel_path=rel,
                        action="conflict",
                        reason=_conflict_reason(rel, prev_files, previous_manifest),
                        sidecar_path=sidecar,
                    ))

    return OverlayPlan(
        target_dir=str(target_dir),
        actions=actions,
    )


def detect_orphans(
    previous_manifest: GenerationManifest | None,
    current_files: set[str],
) -> list[str]:
    """Find files in the previous manifest that are not in the current generation.

    Args:
        previous_manifest: The manifest from the prior generation run.
        current_files: Set of relative paths from the current generation.

    Returns:
        Sorted list of orphaned relative file paths.
    """
    if previous_manifest is None:
        return []
    prev_files = collect_all_wrote_paths(previous_manifest)
    return sorted(prev_files - current_files)


def apply_plan(
    plan: OverlayPlan,
    temp_dir: Path,
    target_dir: Path,
) -> OverlaySummary:
    """Execute the overlay plan: create, skip, write sidecars, or overwrite.

    Args:
        plan: The overlay plan from compare_trees().
        temp_dir: Directory containing freshly generated files.
        target_dir: Existing project directory (overlay target).

    Returns:
        An OverlaySummary with counts and sidecar paths.
    """
    summary = OverlaySummary(
        mode="overlay",
        target_dir=str(target_dir),
        orphaned_files=plan.orphans,
    )

    for action in plan.actions:
        src = temp_dir / action.rel_path
        dst = target_dir / action.rel_path

        if action.action == "create":
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                summary.files_created += 1
            except OSError as exc:
                logger.warning("Write failed for %s: %s", action.rel_path, exc)

        elif action.action == "unchanged":
            summary.files_unchanged += 1

        elif action.action == "conflict":
            summary.files_conflicted += 1
            # Write sidecar
            if action.sidecar_path:
                sidecar_dst = target_dir / action.sidecar_path
                try:
                    sidecar_dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, sidecar_dst)
                    summary.sidecars_written.append(action.sidecar_path)
                except OSError as exc:
                    logger.warning(
                        "Sidecar write failed for %s: %s",
                        action.sidecar_path, exc,
                    )

        elif action.action == "force_overwrite":
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                summary.files_force_overwritten += 1
            except OSError as exc:
                logger.warning("Overwrite failed for %s: %s", action.rel_path, exc)

    return summary


def format_overlay_report(plan: OverlayPlan) -> str:
    """Format a human-readable overlay summary for CLI output.

    Used after apply_plan() for non-dry-run output, and also as the
    body for dry-run reports.
    """
    lines: list[str] = []

    creates = plan.creates
    unchanged = plan.unchanged
    conflicts = plan.conflicts
    force_ow = plan.force_overwrites

    # Summary counts
    if force_ow:
        lines.append("Overlay applied (force mode):")
    else:
        lines.append("Overlay applied:")
    lines.append(f"  Created: {len(creates)} file(s)")
    lines.append(f"  Unchanged: {len(unchanged)} file(s)")

    if force_ow:
        lines.append(f"  Overwritten: {len(force_ow)} file(s)")
    else:
        lines.append(
            f"  Conflicts: {len(conflicts)} file(s)"
            + (" -- sidecars written as .foundry-new" if conflicts else "")
        )

    if plan.orphans:
        lines.append(f"  Orphans: {len(plan.orphans)} file(s)")

    # Conflict / overwrite details
    if conflicts:
        lines.append("")
        lines.append("Conflict details:")
        for c in conflicts:
            lines.append(f"  ! {c.rel_path} -> {c.sidecar_path}")

    if force_ow:
        lines.append("")
        lines.append("Overwrite details:")
        for f in force_ow:
            lines.append(f"  ! {f.rel_path} (overwritten)")

    # Orphan details
    if plan.orphans:
        lines.append("")
        lines.append("Orphaned files (from prior run, not in current composition):")
        for o in plan.orphans:
            lines.append(f"  ? {o}")

    # Total
    total = len(creates) + len(unchanged) + len(conflicts) + len(force_ow)
    lines.append("")
    lines.append(
        f"Total files: {total}"
        f" ({len(creates)} created, {len(unchanged)} unchanged"
        + (f", {len(conflicts)} conflicts" if conflicts else "")
        + (f", {len(force_ow)} overwritten" if force_ow else "")
        + ")"
    )

    return "\n".join(lines)


def format_dry_run_report(plan: OverlayPlan) -> str:
    """Format a detailed dry-run report showing what overlay would do.

    No files are written; this is purely informational.
    """
    lines: list[str] = []
    lines.append(f"Dry-run overlay report for: {plan.target_dir}")

    creates = plan.creates
    unchanged = plan.unchanged
    conflicts = plan.conflicts

    # Would create
    lines.append("")
    lines.append(f"Would create ({len(creates)} file(s)):")
    if creates:
        for a in creates:
            lines.append(f"  + {a.rel_path}")
    else:
        lines.append("  (none)")

    # Would skip -- unchanged
    lines.append("")
    lines.append(f"Would skip -- unchanged ({len(unchanged)} file(s)):")
    if unchanged:
        for a in unchanged:
            lines.append(f"  = {a.rel_path}")
    else:
        lines.append("  (none)")

    # Conflicts
    lines.append("")
    lines.append(f"Conflicts ({len(conflicts)} file(s)):")
    if conflicts:
        for a in conflicts:
            lines.append(f"  ! {a.rel_path}")
            lines.append(f"    Reason: {a.reason}")
            lines.append(f"    Would write sidecar: {a.sidecar_path}")
    else:
        lines.append("  (none)")

    # Orphans
    if plan.orphans:
        lines.append("")
        lines.append(f"Orphaned files ({len(plan.orphans)} file(s)):")
        for o in plan.orphans:
            lines.append(f"  ? {o}")
            lines.append(
                "    Tip: This file was generated by a prior run"
                " but is not in the current composition."
            )

    # Summary line
    lines.append("")
    lines.append(
        f"Summary: {len(creates)} create, {len(unchanged)} unchanged"
        f", {len(conflicts)} conflicts"
        + (f", {len(plan.orphans)} orphan" if plan.orphans else "")
    )
    lines.append("No files were written (dry-run mode).")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _files_identical(path_a: Path, path_b: Path) -> bool:
    """Compare two files byte-for-byte."""
    return path_a.read_bytes() == path_b.read_bytes()


def _conflict_reason(
    rel_path: str,
    prev_files: set[str],
    previous_manifest: GenerationManifest | None,
) -> str:
    """Build a human-readable conflict reason with provenance context."""
    if previous_manifest is not None:
        if rel_path in prev_files:
            return (
                "File was generated by Foundry in a prior run"
                " but has been modified since."
            )
        else:
            return (
                "File exists in the overlay-managed scope"
                " but was not generated by Foundry."
            )
    return "File exists (no prior manifest available to determine origin)."
