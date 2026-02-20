# BEAN-159: Test Seeder Task Numbering Is Gapless with Mixed Personas

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-159 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

When the team includes both known and unknown personas, the seeder should produce gapless sequential task numbers (no skipped IDs from unrecognized personas). No test currently verifies this behavior.

## Goal

Add a test with `["developer", "unknown-role", "architect"]`, extract all row numbers from the output, and assert they form a contiguous 1..N sequence with no gaps. Confirms the counter logic handles adversarial input correctly.

## Scope

### In Scope
- Add a test verifying gapless task numbering with mixed known/unknown personas
- Test with a team list containing an unrecognized persona

### Out of Scope
- Modifying the seeder's numbering logic
- Changing how unknown personas are handled

## Acceptance Criteria

- [ ] Test uses a team list with both known and unknown personas (e.g., `["developer", "unknown-role", "architect"]`)
- [ ] Test extracts row numbers from seeder output and asserts they are contiguous 1..N
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

Ensures counter logic handles adversarial input correctly — no gaps from unrecognized personas.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6997cafe7efb03f79bd2ebcd |
| **Card Name** | Test seeder task numbering is gapless with mixed personas |
| **Card URL** | https://trello.com/c/kYNdilH5/32-test-seeder-task-numbering-is-gapless-with-mixed-personas |

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
