# BEAN-054: Theme Wiring Fix

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-054 |
| **Status** | New |
| **Priority** | High |
| **Created** | 2026-02-08 |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The dark industrial theme (defined in `foundry_app/ui/theme.py`) is not rendering in the application. The screenshot shows a white/light sidebar and unstyled menu bar despite a comprehensive dark palette being defined in code. The root cause is that `apply_theme(app)` is never called in `foundry_app/main.py` after creating the QApplication. Additionally, the MainWindow's own stylesheet may have escaping issues with the f-string double-brace pattern (`{{{{`}`) that could prevent proper QSS rendering.

## Goal

The Foundry application renders with its intended dark industrial palette on startup — deep charcoal backgrounds, brass/gold accents, and properly styled sidebar, menu bar, and content areas. No light/white unstyled regions remain.

## Scope

### In Scope
- Add `theme.apply_theme(app)` call in `foundry_app/main.py` after QApplication creation
- Audit the MainWindow `STYLESHEET` f-string escaping to ensure QSS selectors render correctly
- Verify that sidebar, menu bar, content area, and placeholder screens all pick up the dark theme
- Test that the About dialog still works correctly (it has special light-background handling)
- Ensure no regressions in existing styled screens (Builder wizard, Library Manager, etc.)

### Out of Scope
- New icons or icon integration (that's BEAN-055)
- Removing the menu bar (that's BEAN-056)
- Changing the palette colors themselves (BEAN-045 palette is fine)

## Acceptance Criteria

- [ ] `apply_theme(app)` is called in `main.py` before MainWindow is shown
- [ ] Sidebar renders with dark background (`#141424` BG_INSET) on app startup
- [ ] Navigation items show brass/gold accent on selection and hover
- [ ] Menu bar renders dark, not light/white
- [ ] Content area renders with dark background (`#1a1a2e` BG_BASE)
- [ ] About dialog remains readable (dark text on light native background)
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- This is a defect fix — BEAN-045 and BEAN-046 were marked Done but the theme never rendered because `apply_theme()` was never wired into the startup sequence.
- The _index.md shows BEAN-045/046/047 as "New" but their bean.md files say "Done" — status discrepancy in the index should be reconciled.
- This bean should be completed before BEAN-055 and BEAN-056, as those assume a working dark theme baseline.
