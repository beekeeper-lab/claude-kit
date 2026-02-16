# Task 03: Final Verification

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-124-T03 |
| **Bean** | BEAN-124 |
| **Owner** | tech-qa |
| **Status** | Pending |
| **Depends On** | T01, T02 |

## Description

Run the full test suite and linter to verify all changes are correct and no regressions were introduced.

## Acceptance Criteria

- [ ] `uv run pytest` passes all tests
- [ ] `uv run ruff check foundry_app/` is clean
- [ ] No regressions in other test files
