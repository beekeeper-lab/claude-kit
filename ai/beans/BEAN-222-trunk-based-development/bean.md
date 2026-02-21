# BEAN-222: Move to Trunk-Based Development

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-222 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-02-21 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Process |

## Problem Statement

The current two-branch workflow (`test` → `main`) adds ceremony without value. There is no independent validation, staging environment, or QA gate on the `test` branch — beans merge to `test` then immediately deploy to `main`. This creates unnecessary merge points, complicates the long-run orchestrator, and adds friction to every bean lifecycle.

## Goal

Eliminate the `test` branch and adopt trunk-based development. Feature branches merge directly to `main`. The `/deploy` command becomes a tagging/release tool (or is removed). All skills, commands, agents, and workflow docs are updated to reflect the simplified flow.

## Scope

### In Scope
- Update `/long-run` skill and command (Phase 0 targets `main`, no deploy step)
- Update `/merge-bean` skill and command (default target becomes `main`)
- Update `/spawn-bean` command (worktrees branch from `main`, merge to `main`)
- Update `/deploy` skill and command (repurpose as tag/release, or remove)
- Update bean workflow docs (`ai/context/bean-workflow.md`)
- Update all agent files that reference the `test` branch (`.claude/agents/`)
- Update `CLAUDE.md` if it references the `test` branch workflow
- Update library templates in `ai-team-library/` (long-run, merge-bean, spawn-bean)
- Update MEMORY.md entries that reference `test` branch workflow
- Delete the `test` branch (local and remote) after migration
- Update any hooks that reference the `test` branch

### Out of Scope
- Adding CI/CD pipeline (future bean if needed)
- Changing the bean lifecycle model itself
- Adding branch protection rules

## Acceptance Criteria

- [ ] Feature branches created from `main` and merge directly to `main`
- [ ] `/long-run` works with `main` as the sole integration branch
- [ ] `/merge-bean` defaults to `main`
- [ ] `/deploy` is repurposed or removed
- [ ] All agent files updated (no stale `test` branch references)
- [ ] All skill/command files updated
- [ ] Library templates updated for generated sub-apps
- [ ] Bean workflow docs updated
- [ ] `test` branch deleted (local + remote)
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

This is a process simplification. The test branch has never served as a real integration gate — it's just a pass-through. Trunk-based development with short-lived feature branches is the natural fit for how we actually work.

BEAN-223 (claude subtree sharing) depends on this bean completing first, since the subtree migration will reference the new trunk-based workflow.

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
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |
