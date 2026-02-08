"""Tests for foundry_app.ui.theme — constants, QSS templates, apply_theme."""

from __future__ import annotations

import re

import pytest

from foundry_app.ui import theme

# ---------------------------------------------------------------------------
# Color constants
# ---------------------------------------------------------------------------

_HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


class TestColorPalette:
    """All color constants must be valid 6-digit hex strings."""

    @pytest.mark.parametrize(
        "name",
        [
            "BG_BASE",
            "BG_SURFACE",
            "BG_OVERLAY",
            "BG_INSET",
            "BORDER_DEFAULT",
            "BORDER_SUBTLE",
            "ACCENT_PRIMARY",
            "ACCENT_PRIMARY_HOVER",
            "ACCENT_PRIMARY_MUTED",
            "ACCENT_SECONDARY",
            "ACCENT_SECONDARY_HOVER",
            "ACCENT_SECONDARY_MUTED",
            "TEXT_PRIMARY",
            "TEXT_SECONDARY",
            "TEXT_DISABLED",
            "TEXT_ON_ACCENT",
            "STATUS_SUCCESS",
            "STATUS_ERROR",
            "STATUS_WARNING",
            "STATUS_INFO",
        ],
    )
    def test_color_is_valid_hex(self, name: str) -> None:
        value = getattr(theme, name)
        assert isinstance(value, str)
        assert _HEX_RE.match(value), f"{name} = {value!r} is not a valid hex color"

    def test_bg_base_is_dark(self) -> None:
        """Background should be a dark color (low luminance)."""
        r, g, b = _hex_to_rgb(theme.BG_BASE)
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        assert luminance < 80, (
            f"BG_BASE luminance {luminance} is too bright for a dark theme"
        )

    def test_accent_primary_is_warm(self) -> None:
        """Primary accent should be warm (red channel > blue channel)."""
        r, _g, b = _hex_to_rgb(theme.ACCENT_PRIMARY)
        assert r > b, "ACCENT_PRIMARY should be warm-toned (R > B)"

    def test_accent_secondary_is_cool(self) -> None:
        """Secondary accent should be cool (blue channel > red channel)."""
        r, _g, b = _hex_to_rgb(theme.ACCENT_SECONDARY)
        assert b > r, "ACCENT_SECONDARY should be cool-toned (B > R)"


# ---------------------------------------------------------------------------
# Typography constants
# ---------------------------------------------------------------------------

class TestTypography:
    def test_font_family_is_string(self) -> None:
        assert isinstance(theme.FONT_FAMILY, str)
        assert len(theme.FONT_FAMILY) > 0

    @pytest.mark.parametrize(
        "name,expected_min,expected_max",
        [
            ("FONT_SIZE_XS", 8, 14),
            ("FONT_SIZE_SM", 10, 14),
            ("FONT_SIZE_MD", 12, 16),
            ("FONT_SIZE_LG", 14, 20),
            ("FONT_SIZE_XL", 18, 24),
            ("FONT_SIZE_XXL", 22, 32),
        ],
    )
    def test_font_size_in_range(
        self, name: str, expected_min: int, expected_max: int
    ) -> None:
        value = getattr(theme, name)
        assert isinstance(value, int)
        assert expected_min <= value <= expected_max, (
            f"{name}={value} out of [{expected_min},{expected_max}]"
        )

    def test_font_sizes_are_ascending(self) -> None:
        sizes = [
            theme.FONT_SIZE_XS,
            theme.FONT_SIZE_SM,
            theme.FONT_SIZE_MD,
            theme.FONT_SIZE_LG,
            theme.FONT_SIZE_XL,
            theme.FONT_SIZE_XXL,
        ]
        assert sizes == sorted(sizes), f"Font sizes not ascending: {sizes}"

    @pytest.mark.parametrize(
        "name",
        ["FONT_WEIGHT_NORMAL", "FONT_WEIGHT_MEDIUM", "FONT_WEIGHT_BOLD"],
    )
    def test_font_weight_is_int(self, name: str) -> None:
        value = getattr(theme, name)
        assert isinstance(value, int)
        assert 100 <= value <= 900


# ---------------------------------------------------------------------------
# Spacing constants
# ---------------------------------------------------------------------------

class TestSpacing:
    @pytest.mark.parametrize(
        "name",
        [
            "SPACE_XS",
            "SPACE_SM",
            "SPACE_MD",
            "SPACE_LG",
            "SPACE_XL",
            "SPACE_XXL",
            "RADIUS_SM",
            "RADIUS_MD",
            "RADIUS_LG",
        ],
    )
    def test_spacing_is_positive_int(self, name: str) -> None:
        value = getattr(theme, name)
        assert isinstance(value, int)
        assert value > 0

    def test_spaces_are_ascending(self) -> None:
        spaces = [
            theme.SPACE_XS,
            theme.SPACE_SM,
            theme.SPACE_MD,
            theme.SPACE_LG,
            theme.SPACE_XL,
            theme.SPACE_XXL,
        ]
        assert spaces == sorted(spaces), f"Spaces not ascending: {spaces}"

    def test_radii_are_ascending(self) -> None:
        radii = [theme.RADIUS_SM, theme.RADIUS_MD, theme.RADIUS_LG]
        assert radii == sorted(radii), f"Radii not ascending: {radii}"


# ---------------------------------------------------------------------------
# QSS template strings
# ---------------------------------------------------------------------------

class TestQSSTemplates:
    """Each QSS template must be a non-empty string with expected CSS-like properties."""

    @pytest.mark.parametrize(
        "name,expected_fragments",
        [
            ("QSS_CARD", ["background-color", "border", "border-radius", "padding"]),
            ("QSS_INPUT", ["background-color", "border", "color", "font-size"]),
            (
                "QSS_BUTTON_PRIMARY",
                ["background-color", "color", "border", "font-weight"],
            ),
            ("QSS_BUTTON_SECONDARY", ["color", "border", "font-weight"]),
            ("QSS_SCROLLBAR", ["QScrollBar", "handle", "background"]),
            ("QSS_LIST_ITEM", ["padding", "color", "font-size"]),
            (
                "QSS_SECTION_HEADER",
                ["color", "font-size", "font-weight", "border-bottom"],
            ),
        ],
    )
    def test_qss_contains_expected_properties(
        self, name: str, expected_fragments: list[str]
    ) -> None:
        qss = getattr(theme, name)
        assert isinstance(qss, str)
        assert len(qss.strip()) > 0, f"{name} is empty"
        for frag in expected_fragments:
            assert frag in qss, f"{name} missing expected fragment {frag!r}"

    @pytest.mark.parametrize(
        "name",
        [
            "QSS_CARD",
            "QSS_INPUT",
            "QSS_BUTTON_PRIMARY",
            "QSS_BUTTON_SECONDARY",
            "QSS_SCROLLBAR",
            "QSS_LIST_ITEM",
            "QSS_SECTION_HEADER",
        ],
    )
    def test_qss_uses_theme_colors(self, name: str) -> None:
        """QSS templates should reference actual theme color values."""
        qss = getattr(theme, name)
        all_colors = [
            theme.BG_BASE,
            theme.BG_SURFACE,
            theme.BG_OVERLAY,
            theme.BG_INSET,
            theme.BORDER_DEFAULT,
            theme.BORDER_SUBTLE,
            theme.ACCENT_PRIMARY,
            theme.ACCENT_SECONDARY,
            theme.ACCENT_SECONDARY_MUTED,
            theme.TEXT_PRIMARY,
            theme.TEXT_SECONDARY,
            theme.TEXT_ON_ACCENT,
        ]
        found = any(c in qss for c in all_colors)
        assert found, f"{name} does not reference any theme color constants"


# ---------------------------------------------------------------------------
# apply_theme()
# ---------------------------------------------------------------------------

class TestApplyTheme:
    def test_apply_theme_sets_stylesheet(self) -> None:
        """apply_theme should call setStyleSheet on the provided object."""

        class FakeApp:
            stylesheet: str = ""

            def setStyleSheet(self, ss: str) -> None:  # noqa: N802
                self.stylesheet = ss

        app = FakeApp()
        theme.apply_theme(app)
        assert len(app.stylesheet) > 0, "Stylesheet was not applied"
        assert theme.BG_BASE in app.stylesheet
        assert "QMainWindow" in app.stylesheet

    def test_apply_theme_callable(self) -> None:
        """apply_theme must be a callable."""
        assert callable(theme.apply_theme)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert '#RRGGBB' to (R, G, B) integers."""
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
