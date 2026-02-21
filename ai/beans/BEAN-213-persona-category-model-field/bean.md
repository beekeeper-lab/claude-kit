# BEAN-213: Add Category Field to PersonaInfo Model

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-213 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-21 |
| **Started** | 2026-02-20 20:49 |
| **Completed** | 2026-02-20 20:52 |
| **Duration** | 3m |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

With 24 personas in the library, the flat list in the Foundry wizard is hard to navigate. To support grouped display in the UI, the data model and library indexer need to carry a `category` field for each persona. Currently `PersonaInfo` has no category field, and `_scan_personas()` does not parse any category metadata from persona files.

## Goal

Add a `category` string field to the `PersonaInfo` Pydantic model and update the library indexer's `_scan_personas()` function to parse a `## Category` section from each persona's `persona.md` file. Personas without a Category section default to an empty string.

## Scope

### In Scope
- Add `category: str = ""` field to `PersonaInfo` in `foundry_app/core/models.py`
- Update `_scan_personas()` in `foundry_app/services/library_indexer.py` to parse `## Category` from persona.md (same pattern used for hook pack categories)
- Update tests in `tests/test_library_indexer.py` to assert category values
- Update tests in `tests/test_models.py` if PersonaInfo validation tests exist

### Out of Scope
- Modifying persona.md files in ai-team-library (that's BEAN-214)
- UI changes (that's BEAN-215)
- Adding category to stacks or hook packs

## Acceptance Criteria

- [x] `PersonaInfo` model has a `category` field of type `str` with default `""`
- [x] `_scan_personas()` reads `## Category` section from persona.md and populates the field
- [x] Personas without a `## Category` section get `category = ""`
- [x] Existing graceful degradation tests still pass (missing dirs, empty dirs, etc.)
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add `category` field to PersonaInfo model | Developer | — | Done |
| 2 | Add `_parse_persona_category()` and update `_scan_personas()` | Developer | 1 | Done |
| 3 | Add/update tests for category parsing | Developer | 2 | Done |
| 4 | Run full test suite and lint check | Tech-QA | 3 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

This bean is a prerequisite for BEAN-214 (category metadata in persona files) and BEAN-215 (grouped UI). The parsing approach mirrors how hook pack categories are already parsed in `_scan_hook_packs()`.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Add `category` field to PersonaInfo model | Developer | — | — | — | — |
| 2 | Add `_parse_persona_category()` and update `_scan_personas()` | Developer | — | — | — | — |
| 3 | Add/update tests for category parsing | Developer | — | — | — | — |
| 4 | Run full test suite and lint check | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 4 |
| **Total Duration** | 3m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |