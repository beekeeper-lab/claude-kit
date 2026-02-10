"""Tests for foundry_app.core.resources — resource path resolution."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from foundry_app.core.resources import get_resource_path


class TestGetResourcePath:

    def test_dev_path_found(self, tmp_path: Path):
        """get_resource_path returns dev path when file exists in project root."""
        # Create a file at the dev path location
        resource_file = tmp_path / "resources" / "icons" / "logo.png"
        resource_file.parent.mkdir(parents=True)
        resource_file.write_bytes(b"PNG")

        with patch("foundry_app.core.resources._PROJECT_ROOT", tmp_path):
            result = get_resource_path("resources/icons/logo.png")

        assert result == resource_file
        assert result.is_file()

    def test_bundled_fallback(self, tmp_path: Path):
        """get_resource_path falls back to bundled path when dev path missing."""
        # Set up a fake project root with no dev file
        fake_project = tmp_path / "project"
        fake_project.mkdir()

        # Set up a fake app dir with bundled resources
        fake_app = tmp_path / "app"
        bundled = fake_app / "_resources" / "icons" / "logo.png"
        bundled.parent.mkdir(parents=True)
        bundled.write_bytes(b"PNG-bundled")

        with (
            patch("foundry_app.core.resources._PROJECT_ROOT", fake_project),
            patch("foundry_app.core.resources._BUNDLED_RESOURCES", fake_app / "_resources"),
        ):
            result = get_resource_path("resources/icons/logo.png")

        assert result == bundled
        assert result.is_file()

    def test_neither_found_returns_dev_path(self, tmp_path: Path):
        """get_resource_path returns dev path when neither exists, with warning."""
        fake_project = tmp_path / "project"
        fake_project.mkdir()
        fake_app = tmp_path / "app"
        fake_app.mkdir()

        with (
            patch("foundry_app.core.resources._PROJECT_ROOT", fake_project),
            patch("foundry_app.core.resources._BUNDLED_RESOURCES", fake_app / "_resources"),
            patch("foundry_app.core.resources.logger") as mock_logger,
        ):
            result = get_resource_path("resources/icons/logo.png")

        # Returns the dev path even though it doesn't exist
        assert result == fake_project / "resources" / "icons" / "logo.png"
        assert not result.is_file()
        mock_logger.warning.assert_called_once()

    def test_non_resources_prefix_skips_bundled(self, tmp_path: Path):
        """Paths not starting with 'resources/' never check bundled dir."""
        fake_project = tmp_path / "project"
        fake_project.mkdir()
        fake_app = tmp_path / "app"
        fake_app.mkdir()

        with (
            patch("foundry_app.core.resources._PROJECT_ROOT", fake_project),
            patch("foundry_app.core.resources._BUNDLED_RESOURCES", fake_app / "_resources"),
            patch("foundry_app.core.resources.logger") as mock_logger,
        ):
            result = get_resource_path("other/file.txt")

        # Falls through to dev path without checking bundled
        assert result == fake_project / "other" / "file.txt"
        mock_logger.warning.assert_called_once()
