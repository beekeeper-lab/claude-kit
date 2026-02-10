"""Tests for BEAN-109: Library Manager — Hook Create.

Verifies that hooks can be created via the Library Manager: name input
validation, starter content written to disk, and the new hook appears
in the file tree.

These tests mock PySide6 so they can run without libGL.so.1.
Follows the pattern of tests/test_command_create.py.
"""

from __future__ import annotations

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
    starter_content,
    validate_asset_name,
)


def _create_library(root: Path) -> Path:
    """Create a minimal library with a hooks directory."""
    lib = root / "test-library"
    (lib / "personas" / "dev").mkdir(parents=True)
    (lib / "personas" / "dev" / "persona.md").write_text("# Dev", encoding="utf-8")
    (lib / "stacks").mkdir(parents=True)
    (lib / "templates").mkdir(parents=True)
    (lib / "workflows").mkdir(parents=True)
    hooks_dir = lib / "claude" / "hooks"
    hooks_dir.mkdir(parents=True)
    (hooks_dir / "pre-commit-lint.md").write_text(
        "# Hook Pack: Pre Commit Lint\n\nLint hook.", encoding="utf-8"
    )
    (lib / "claude" / "commands").mkdir(parents=True)
    (lib / "claude" / "commands" / "review-pr.md").write_text(
        "# Review PR", encoding="utf-8"
    )
    (lib / "claude" / "skills" / "handoff").mkdir(parents=True)
    (lib / "claude" / "skills" / "handoff" / "SKILL.md").write_text(
        "# Handoff", encoding="utf-8"
    )
    return lib


# ---------------------------------------------------------------------------
# Starter content
# ---------------------------------------------------------------------------


class TestHookStarterContent:

    def test_starter_content_uses_hook_template(self):
        content = starter_content("Claude Hooks", "security-scan")
        assert "# Hook Pack: Security Scan" in content

    def test_starter_content_contains_all_sections(self):
        content = starter_content("Claude Hooks", "my-hook")
        assert "## Purpose" in content
        assert "## Hooks" in content
        assert "## Configuration" in content
        assert "## Posture Compatibility" in content

    def test_starter_content_title_cases_name(self):
        """Hook names should be title-cased in the heading."""
        content = starter_content("Claude Hooks", "pre-deploy-check")
        assert "# Hook Pack: Pre Deploy Check" in content

    def test_starter_content_has_hook_table(self):
        content = starter_content("Claude Hooks", "lint-gate")
        assert "Hook Name" in content
        assert "Trigger" in content
        assert "Fail Action" in content

    def test_starter_content_has_posture_table(self):
        content = starter_content("Claude Hooks", "lint-gate")
        assert "strict" in content
        assert "standard" in content
        assert "relaxed" in content


# ---------------------------------------------------------------------------
# Name validation
# ---------------------------------------------------------------------------


class TestHookNameValidation:

    def test_valid_hook_name(self):
        assert validate_asset_name("security-scan") is None

    def test_valid_single_word(self):
        assert validate_asset_name("lint") is None

    def test_valid_with_digits(self):
        assert validate_asset_name("v2-hook") is None

    def test_rejects_uppercase(self):
        assert validate_asset_name("SecurityScan") is not None

    def test_rejects_spaces(self):
        assert validate_asset_name("security scan") is not None

    def test_rejects_underscores(self):
        assert validate_asset_name("security_scan") is not None

    def test_rejects_empty(self):
        assert validate_asset_name("") is not None

    def test_rejects_too_long(self):
        assert validate_asset_name("a" * 61) is not None

    def test_accepts_max_length(self):
        assert validate_asset_name("a" * 60) is None


# ---------------------------------------------------------------------------
# File creation on disk (simulating the _on_new_asset flow)
# ---------------------------------------------------------------------------


class TestHookFileCreation:

    def test_create_hook_file_on_disk(self, tmp_path: Path):
        """Simulate the create-hook flow: write starter content to disk."""
        lib = _create_library(tmp_path)
        name = "post-deploy-notify"
        target_dir = lib / "claude" / "hooks"
        dest = target_dir / f"{name}.md"

        assert not dest.exists()
        content = starter_content("Claude Hooks", name)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")

        assert dest.is_file()
        written = dest.read_text(encoding="utf-8")
        assert "# Hook Pack: Post Deploy Notify" in written
        assert "## Purpose" in written

    def test_duplicate_detection(self, tmp_path: Path):
        """Duplicate name check: file already exists on disk."""
        lib = _create_library(tmp_path)
        existing = lib / "claude" / "hooks" / "pre-commit-lint.md"
        assert existing.exists(), "pre-commit-lint.md should already exist"

    def test_new_hook_appears_in_tree(self, tmp_path: Path):
        """After creating a file, _build_file_tree should include it."""
        lib = _create_library(tmp_path)
        name = "brand-new-hook"
        dest = lib / "claude" / "hooks" / f"{name}.md"
        dest.write_text(
            starter_content("Claude Hooks", name), encoding="utf-8"
        )

        tree = _build_file_tree(lib)
        hooks_cat = next(c for c in tree if c["name"] == "Claude Hooks")
        child_names = [ch["name"] for ch in hooks_cat["children"]]
        assert "brand-new-hook.md" in child_names

    def test_new_hook_has_file_path_in_tree(self, tmp_path: Path):
        """The tree node for the new hook should carry the file path."""
        lib = _create_library(tmp_path)
        name = "path-check"
        dest = lib / "claude" / "hooks" / f"{name}.md"
        dest.write_text(
            starter_content("Claude Hooks", name), encoding="utf-8"
        )

        tree = _build_file_tree(lib)
        hooks_cat = next(c for c in tree if c["name"] == "Claude Hooks")
        node = next(
            ch for ch in hooks_cat["children"] if ch["name"] == "path-check.md"
        )
        assert node["path"] == str(dest)

    def test_tree_sorted_after_creation(self, tmp_path: Path):
        """Hooks should appear sorted alphabetically in the tree."""
        lib = _create_library(tmp_path)
        for name in ["alpha-hook", "zebra-hook"]:
            dest = lib / "claude" / "hooks" / f"{name}.md"
            dest.write_text(
                starter_content("Claude Hooks", name), encoding="utf-8"
            )

        tree = _build_file_tree(lib)
        hooks_cat = next(c for c in tree if c["name"] == "Claude Hooks")
        names = [ch["name"] for ch in hooks_cat["children"]]
        assert names == sorted(names)
        assert "alpha-hook.md" in names
        assert "pre-commit-lint.md" in names
        assert "zebra-hook.md" in names

    def test_hook_file_is_leaf_node(self, tmp_path: Path):
        """Hook files should be leaf nodes (path set, no children)."""
        lib = _create_library(tmp_path)
        name = "leaf-check"
        dest = lib / "claude" / "hooks" / f"{name}.md"
        dest.write_text(
            starter_content("Claude Hooks", name), encoding="utf-8"
        )

        tree = _build_file_tree(lib)
        hooks_cat = next(c for c in tree if c["name"] == "Claude Hooks")
        node = next(
            ch for ch in hooks_cat["children"] if ch["name"] == "leaf-check.md"
        )
        assert node["path"] is not None
        assert node.get("children", []) == []
