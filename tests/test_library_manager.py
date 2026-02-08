"""Tests for foundry_app.ui.screens.library_manager — tree browser and preview."""

from pathlib import Path

from PySide6.QtWidgets import QApplication

from foundry_app.ui.screens.library_manager import (
    LibraryManagerScreen,
    _build_file_tree,
)

_app = QApplication.instance() or QApplication([])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_library(root: Path) -> Path:
    """Create a minimal library directory structure for testing."""
    lib = root / "test-library"
    # Personas
    persona_dir = lib / "personas" / "developer"
    persona_dir.mkdir(parents=True)
    (persona_dir / "persona.md").write_text("# Developer persona", encoding="utf-8")
    (persona_dir / "outputs.md").write_text("# Outputs", encoding="utf-8")
    templates_dir = persona_dir / "templates"
    templates_dir.mkdir()
    (templates_dir / "impl.md.j2").write_text("template", encoding="utf-8")

    # Stacks
    stack_dir = lib / "stacks" / "python-fastapi"
    stack_dir.mkdir(parents=True)
    (stack_dir / "stack.md").write_text("# Python + FastAPI", encoding="utf-8")

    # Shared Templates
    tpl_dir = lib / "templates"
    tpl_dir.mkdir(parents=True)
    (tpl_dir / "CLAUDE.md.j2").write_text("# Claude template", encoding="utf-8")

    # Workflows
    wf_dir = lib / "workflows"
    wf_dir.mkdir(parents=True)
    (wf_dir / "default.md").write_text("# Default workflow", encoding="utf-8")

    # Claude assets
    cmd_dir = lib / "claude" / "commands"
    cmd_dir.mkdir(parents=True)
    (cmd_dir / "review-pr.md").write_text("# Review PR", encoding="utf-8")

    skills_dir = lib / "claude" / "skills" / "handoff"
    skills_dir.mkdir(parents=True)
    (skills_dir / "SKILL.md").write_text("# Handoff skill", encoding="utf-8")

    hooks_dir = lib / "claude" / "hooks"
    hooks_dir.mkdir(parents=True)
    (hooks_dir / "pre-commit-lint.md").write_text("# Lint hook", encoding="utf-8")

    return lib


# ---------------------------------------------------------------------------
# Pure tree building logic
# ---------------------------------------------------------------------------


class TestBuildFileTree:

    def test_empty_dir(self, tmp_path: Path):
        tree = _build_file_tree(tmp_path / "nonexistent")
        assert tree == []

    def test_returns_all_categories(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        tree = _build_file_tree(lib)
        names = [cat["name"] for cat in tree]
        assert "Personas" in names
        assert "Stacks" in names
        assert "Shared Templates" in names
        assert "Workflows" in names
        assert "Claude Commands" in names
        assert "Claude Skills" in names
        assert "Claude Hooks" in names

    def test_personas_has_children(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        assert len(personas["children"]) == 1
        dev = personas["children"][0]
        assert dev["name"] == "developer"
        # developer dir should have persona.md, outputs.md, and templates/ subdir
        child_names = [c["name"] for c in dev["children"]]
        assert "persona.md" in child_names
        assert "outputs.md" in child_names
        assert "templates" in child_names

    def test_file_nodes_have_paths(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        dev = personas["children"][0]
        persona_md = next(c for c in dev["children"] if c["name"] == "persona.md")
        assert persona_md["path"] is not None
        assert persona_md["path"].endswith("persona.md")

    def test_directory_nodes_have_no_path(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        dev = personas["children"][0]
        assert dev["path"] is None

    def test_missing_category_dir_gives_empty_children(self, tmp_path: Path):
        lib = tmp_path / "sparse-lib"
        (lib / "personas" / "test").mkdir(parents=True)
        (lib / "personas" / "test" / "persona.md").write_text("hi", encoding="utf-8")
        tree = _build_file_tree(lib)
        stacks = next(c for c in tree if c["name"] == "Stacks")
        assert stacks["children"] == []

    def test_hidden_files_are_skipped(self, tmp_path: Path):
        lib = tmp_path / "lib"
        wf = lib / "workflows"
        wf.mkdir(parents=True)
        (wf / ".hidden").write_text("nope", encoding="utf-8")
        (wf / "visible.md").write_text("yes", encoding="utf-8")
        tree = _build_file_tree(lib)
        workflows = next(c for c in tree if c["name"] == "Workflows")
        names = [c["name"] for c in workflows["children"]]
        assert ".hidden" not in names
        assert "visible.md" in names


# ---------------------------------------------------------------------------
# Screen construction
# ---------------------------------------------------------------------------


class TestScreenConstruction:

    def test_creates_screen(self):
        screen = LibraryManagerScreen()
        assert screen is not None

    def test_has_tree(self):
        screen = LibraryManagerScreen()
        assert screen.tree is not None

    def test_has_preview(self):
        screen = LibraryManagerScreen()
        assert screen.preview is not None
        assert screen.preview.isReadOnly()

    def test_has_file_label(self):
        screen = LibraryManagerScreen()
        assert screen.file_label is not None

    def test_has_empty_label(self):
        screen = LibraryManagerScreen()
        assert screen.empty_label is not None


# ---------------------------------------------------------------------------
# Library loading
# ---------------------------------------------------------------------------


class TestLibraryLoading:

    def test_set_library_root(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        assert screen.tree.topLevelItemCount() == 7  # all categories

    def test_nonexistent_root_shows_empty(self, tmp_path: Path):
        screen = LibraryManagerScreen()
        screen.set_library_root(tmp_path / "nonexistent")
        assert screen.tree.topLevelItemCount() == 0
        assert screen.empty_label.isVisible()

    def test_valid_root_hides_empty_label(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        assert not screen.empty_label.isVisible()

    def test_tree_has_correct_nesting(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        personas_item = screen.tree.topLevelItem(0)
        assert personas_item.text(0) == "Personas"
        assert personas_item.childCount() == 1
        dev_item = personas_item.child(0)
        assert dev_item.text(0) == "developer"

    def test_empty_string_root_shows_empty(self):
        screen = LibraryManagerScreen()
        screen.set_library_root("")
        assert screen.tree.topLevelItemCount() == 0

    def test_refresh_updates_tree(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        # Add a new file
        (lib / "workflows" / "new-workflow.md").write_text("new", encoding="utf-8")
        screen.refresh_tree()
        workflows = None
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Workflows":
                workflows = item
                break
        assert workflows is not None
        assert workflows.childCount() == 2


# ---------------------------------------------------------------------------
# File preview
# ---------------------------------------------------------------------------


class TestFilePreview:

    def test_selecting_file_shows_content(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        # Navigate to personas > developer > persona.md
        personas_item = screen.tree.topLevelItem(0)
        dev_item = personas_item.child(0)
        # Find persona.md child
        for i in range(dev_item.childCount()):
            child = dev_item.child(i)
            if child.text(0) == "persona.md":
                screen.tree.setCurrentItem(child)
                break
        assert "Developer persona" in screen.preview.toPlainText()

    def test_selecting_directory_clears_preview(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        # Select a directory node (category)
        personas_item = screen.tree.topLevelItem(0)
        screen.tree.setCurrentItem(personas_item)
        assert screen.preview.toPlainText() == ""

    def test_file_label_shows_path(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        personas_item = screen.tree.topLevelItem(0)
        dev_item = personas_item.child(0)
        for i in range(dev_item.childCount()):
            child = dev_item.child(i)
            if child.text(0) == "persona.md":
                screen.tree.setCurrentItem(child)
                break
        assert "persona.md" in screen.file_label.text()
