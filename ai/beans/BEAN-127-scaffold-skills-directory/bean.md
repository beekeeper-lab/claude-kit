# BEAN-127: Scaffold Skills Directory

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-127 |
| **Status** | Approved |
| **Priority** | Low |
| **Created** | 2026-02-15 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The scaffold service creates `.claude/agents/`, `.claude/commands/`, and `.claude/hooks/` directories but does NOT create `.claude/skills/`. The skills directory only gets created implicitly by the asset copier when it copies skill files. If the asset copier stage fails or if there are no skills to copy, the skills directory won't exist in the output, breaking the expected directory structure.

## Goal

The scaffold service creates `.claude/skills/` alongside the other `.claude/` subdirectories, ensuring the directory structure is consistent regardless of which later stages succeed.

## Scope

### In Scope
- Add `.claude/skills/` to the scaffold service's directory list
- Update scaffold tests to verify the skills directory is created

### Out of Scope
- Changing what the asset copier does
- Adding other missing directories

## Acceptance Criteria

- [ ] `.claude/skills/` is created by the scaffold service
- [ ] Scaffold test verifies the skills directory exists in the output
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Quick fix — likely a one-line addition to `scaffold.py` plus a test assertion
- Related to BEAN-026 (Scaffold Service) which created the original scaffold

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 |      |       |          |           |            |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
