# BEAN-160: Test SecretPolicy Reports Correct Index for Invalid Regex

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-160 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

`SecretPolicy.validate_secret_patterns` embeds the zero-based index of the failing pattern in the error message (`secret_patterns[2]`). Existing tests confirm validation fails but never check the index is correct. Users debugging rejected configs need accurate location info.

## Goal

Add a parameterized test with the invalid pattern at different positions and assert the error message contains the right index.

## Scope

### In Scope
- Add parameterized test for `SecretPolicy.validate_secret_patterns` index reporting
- Test with invalid regex at positions 0, 1, 2+ to verify index accuracy

### Out of Scope
- Modifying the SecretPolicy validation logic
- Changing error message format

## Acceptance Criteria

- [ ] Parameterized test places an invalid regex at different positions in the `secret_patterns` list
- [ ] Each test case asserts the error message contains `secret_patterns[N]` with the correct index N
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

Ensures error messages give actionable location info for debugging rejected configs.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6997caff7b5018d5f44cc603 |
| **Card Name** | Test SecretPolicy reports correct index for invalid regex |
| **Card URL** | https://trello.com/c/0mJIdrhA/33-test-secretpolicy-reports-correct-index-for-invalid-regex |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 |      |       |          |           |            |      |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |
