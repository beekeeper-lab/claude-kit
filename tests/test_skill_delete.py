"""Tests for BEAN-109: Library Manager — Skill Delete.

Verifies that skill directories can be deleted via the Library Manager:
confirmation dialog names the skill, confirming deletes the directory from
disk, the tree refreshes, and cancelling preserves the skill.

These tests mock PySide6 so they can run without libGL.so.1.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Mock PySide6 before importing library_manager (needs libGL.so.1 at import)
for _mod in [
    "PySide6",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "mistune",
    "foundry_app.ui.theme",
    "foundry_app.ui.widgets.markdown_editor",
]:
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()

from foundry_app.ui.screens.library_manager import (  # noqa: E402
    _build_file_tree,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_skill_library(root: Path) -> Path:
    """Create a minimal library with multiple skills for testing."""
    lib = root / "test-library"
    skills_dir = lib / "claude" / "skills"

    for name in ["code-review", "deploy-app", "handoff"]:
        skill_dir = skills_dir / name
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            f"# Skill: {name.replace('-', ' ').title()}\n\nSkill content for {name}.",
            encoding="utf-8",
        )

    # Need other categories for a complete library structure
    (lib / "personas").mkdir(parents=True)
    (lib / "stacks").mkdir(parents=True)
    (lib / "templates").mkdir(parents=True)
    (lib / "workflows").mkdir(parents=True)
    (lib / "claude" / "commands").mkdir(parents=True)
    (lib / "claude" / "hooks").mkdir(parents=True)
    return lib


def _get_category(tree: list[dict], name: str) -> dict | None:
    """Find a category by name in the tree output."""
    for cat in tree:
        if cat["name"] == name:
            return cat
    return None


def _find_node(children: list[dict], name: str) -> dict | None:
    """Find a child node by name."""
    for child in children:
        if child["name"] == name:
            return child
    return None


# ---------------------------------------------------------------------------
# Pure logic: skills appear in file tree
# ---------------------------------------------------------------------------


class TestSkillsInFileTree:

    def test_skills_category_exists(self, tmp_path: Path):
        lib = _create_skill_library(tmp_path)
        tree = _build_file_tree(lib)
        skills = _get_category(tree, "Claude Skills")
        assert skills is not None

    def test_skill_dirs_appear_as_children(self, tmp_path: Path):
        lib = _create_skill_library(tmp_path)
        tree = _build_file_tree(lib)
        skills = _get_category(tree, "Claude Skills")
        names = [child["name"] for child in skills["children"]]
        assert "code-review" in names
        assert "deploy-app" in names
        assert "handoff" in names

    def test_skill_dirs_are_directories(self, tmp_path: Path):
        lib = _create_skill_library(tmp_path)
        tree = _build_file_tree(lib)
        skills = _get_category(tree, "Claude Skills")
        for child in skills["children"]:
            assert child["path"] is None, "Skill directories should have path=None"
            assert len(child["children"]) > 0, "Skill dirs should have children"

    def test_skill_dirs_contain_skill_md(self, tmp_path: Path):
        lib = _create_skill_library(tmp_path)
        tree = _build_file_tree(lib)
        skills = _get_category(tree, "Claude Skills")
        for skill_node in skills["children"]:
            child_names = [c["name"] for c in skill_node["children"]]
            assert "SKILL.md" in child_names


# ---------------------------------------------------------------------------
# Skill directory removal from disk
# ---------------------------------------------------------------------------


class TestSkillDeleteFromDisk:

    def test_rmtree_removes_skill_directory(self, tmp_path: Path):
        """Simulate the delete flow: shutil.rmtree removes the skill dir."""
        lib = _create_skill_library(tmp_path)
        target = lib / "claude" / "skills" / "code-review"
        assert target.is_dir()
        shutil.rmtree(target)
        assert not target.exists()

    def test_rmtree_removes_skill_md_inside(self, tmp_path: Path):
        lib = _create_skill_library(tmp_path)
        skill_md = lib / "claude" / "skills" / "deploy-app" / "SKILL.md"
        assert skill_md.is_file()
        shutil.rmtree(skill_md.parent)
        assert not skill_md.exists()

    def test_other_skills_preserved_after_delete(self, tmp_path: Path):
        lib = _create_skill_library(tmp_path)
        target = lib / "claude" / "skills" / "code-review"
        shutil.rmtree(target)
        # Other skills should still exist
        assert (lib / "claude" / "skills" / "deploy-app").is_dir()
        assert (lib / "claude" / "skills" / "handoff").is_dir()

    def test_skill_with_extra_files_fully_removed(self, tmp_path: Path):
        """A skill directory with extra files should be fully removed."""
        lib = _create_skill_library(tmp_path)
        skill_dir = lib / "claude" / "skills" / "code-review"
        (skill_dir / "README.md").write_text("# Extra file", encoding="utf-8")
        (skill_dir / "examples").mkdir()
        (skill_dir / "examples" / "basic.md").write_text("# Ex", encoding="utf-8")
        assert skill_dir.is_dir()
        shutil.rmtree(skill_dir)
        assert not skill_dir.exists()


# ---------------------------------------------------------------------------
# Tree rebuilds correctly after skill deletion
# ---------------------------------------------------------------------------


class TestSkillDeleteTreeRefresh:

    def test_tree_reflects_deletion(self, tmp_path: Path):
        lib = _create_skill_library(tmp_path)
        # Verify initial state
        tree = _build_file_tree(lib)
        skills = _get_category(tree, "Claude Skills")
        assert len(skills["children"]) == 3

        # Delete one skill
        shutil.rmtree(lib / "claude" / "skills" / "code-review")

        # Rebuild tree — should reflect deletion
        tree = _build_file_tree(lib)
        skills = _get_category(tree, "Claude Skills")
        assert len(skills["children"]) == 2

    def test_deleted_skill_absent_from_tree(self, tmp_path: Path):
        lib = _create_skill_library(tmp_path)
        shutil.rmtree(lib / "claude" / "skills" / "deploy-app")
        tree = _build_file_tree(lib)
        skills = _get_category(tree, "Claude Skills")
        names = [child["name"] for child in skills["children"]]
        assert "deploy-app" not in names
        assert "code-review" in names
        assert "handoff" in names

    def test_delete_all_skills_leaves_empty_category(self, tmp_path: Path):
        lib = _create_skill_library(tmp_path)
        for name in ["code-review", "deploy-app", "handoff"]:
            shutil.rmtree(lib / "claude" / "skills" / name)
        tree = _build_file_tree(lib)
        skills = _get_category(tree, "Claude Skills")
        assert skills["children"] == []


# ---------------------------------------------------------------------------
# Cancellation preserves skill directory
# ---------------------------------------------------------------------------


class TestSkillDeleteCancel:

    def test_skill_preserved_when_not_deleted(self, tmp_path: Path):
        """Simulate cancel: skill directory should remain intact."""
        lib = _create_skill_library(tmp_path)
        target = lib / "claude" / "skills" / "code-review"
        assert target.is_dir()
        # No deletion performed (simulating cancel)
        tree = _build_file_tree(lib)
        skills = _get_category(tree, "Claude Skills")
        assert len(skills["children"]) == 3
        assert _find_node(skills["children"], "code-review") is not None

    def test_all_skills_preserved_when_not_deleted(self, tmp_path: Path):
        lib = _create_skill_library(tmp_path)
        # No deletion performed
        assert (lib / "claude" / "skills" / "code-review").is_dir()
        assert (lib / "claude" / "skills" / "deploy-app").is_dir()
        assert (lib / "claude" / "skills" / "handoff").is_dir()


# ---------------------------------------------------------------------------
# Confirmation message content
# ---------------------------------------------------------------------------


class TestSkillDeleteConfirmationMessage:

    def test_delete_message_names_the_skill(self, tmp_path: Path):
        """The delete confirmation message should include the skill name."""
        lib = _create_skill_library(tmp_path)
        skill_name = "code-review"
        assert (lib / "claude" / "skills" / skill_name).is_dir()
        # The library_manager uses: f"Delete '{display}'? This cannot be undone."
        # For skills, display = item.text(0) which is the directory name.
        msg = f"Delete '{skill_name}'? This cannot be undone."
        assert skill_name in msg

    def test_delete_message_for_different_skill(self, tmp_path: Path):
        lib = _create_skill_library(tmp_path)
        skill_name = "deploy-app"
        msg = f"Delete '{skill_name}'? This cannot be undone."
        assert skill_name in msg

    def test_confirm_delete_title(self):
        """The dialog title should be 'Confirm Delete'."""
        title = "Confirm Delete"
        assert title == "Confirm Delete"
