# Task 2: Verify Quality and Run Tests

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-207-T2 |
| **Owner** | Tech-QA |
| **Status** | Pending |
| **Depends On** | T1 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Description

Verify the finops stack files meet quality standards and all existing tests continue to pass.

## Inputs

- Stack files from Task 1
- Bean acceptance criteria

## Checks

- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)
- [ ] Stack files follow standardized template structure
- [ ] All required topics covered per bean scope