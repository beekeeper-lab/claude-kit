# Task 003: Verify Tests and Lint

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-192-T003 |
| **Title** | Verify all tests pass and lint clean |
| **Owner** | Tech-QA |
| **Status** | Pending |
| **Depends On** | T002 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Objective

Run the full test suite and linter to verify the new persona integrates correctly with the library indexer and no regressions are introduced.

## Acceptance Criteria

- [ ] `uv run pytest` passes all tests
- [ ] `uv run ruff check foundry_app/` reports no issues