# BEAN-218: Add Category Field to ExpertiseInfo Model

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-218 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-21 |
| **Started** | 2026-02-20 21:34 |
| **Completed** | 2026-02-20 21:36 |
| **Duration** | 2m |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

To support grouped display of expertise items in the Foundry wizard, the data model and library indexer need to carry a `category` field for each expertise item. After BEAN-216/217 rename, `ExpertiseInfo` has no category field, and `_scan_expertise()` does not parse any category metadata.

## Goal

Add a `category` string field to `ExpertiseInfo` in models.py and update `_scan_expertise()` in library_indexer.py to parse a `## Category` section from the first markdown file in each expertise directory (e.g., `conventions.md`). Items without a Category section default to empty string.

## Scope

### In Scope
- Add `category: str = ""` field to `ExpertiseInfo` in `foundry_app/core/models.py`
- Update `_scan_expertise()` in `foundry_app/services/library_indexer.py` to parse `## Category` from the first `.md` file in each expertise directory
- Update tests in `tests/test_library_indexer.py` to assert category values
- Add graceful degradation test for expertise items without categories

### Out of Scope
- Adding category metadata to the actual expertise files (that's BEAN-219)
- UI changes (that's BEAN-220)
- Persona categories (those are BEAN-213-215)

## Acceptance Criteria

- [ ] `ExpertiseInfo` model has a `category` field of type `str` with default `""`
- [ ] `_scan_expertise()` reads `## Category` section from expertise files and populates the field
- [ ] Expertise items without a `## Category` section get `category = ""`
- [ ] Existing graceful degradation tests still pass
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Depends on BEAN-216 (codebase rename) and BEAN-217 (library directory rename). The parsing approach mirrors how hook pack categories and persona categories are parsed.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 |      |       |          |           |            |      |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | 2m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |
