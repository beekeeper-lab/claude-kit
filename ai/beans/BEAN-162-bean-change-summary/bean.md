# BEAN-162: Bean Change Summary Section

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-162 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Process |

## Problem Statement

When a team finishes a bean, there is no record of exactly what files and code changed. The user wants to track the implementation diff for each bean to understand the concrete impact of the work.

## Goal

After a bean is completed, generate a git diff summary and add it as a new `## Changes` section in the bean's `bean.md`. This should list files changed and a concise description of what changed in each.

## Scope

### In Scope
- Add a `## Changes` section to the bean template
- Update the merge-bean or long-run workflow to populate the Changes section from `git diff` when a bean is completed
- Include: files changed (with +/- line counts), brief description of changes per file

### Out of Scope
- Retroactively populating Changes for already-completed beans
- Full inline diffs (just summaries)

## Acceptance Criteria

- [ ] Bean template includes a `## Changes` section placeholder
- [ ] When a bean is completed and merged, the Changes section is populated with a git diff summary
- [ ] Changes section lists files modified with line count deltas
- [ ] The workflow update is documented (which step populates the section)
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

The git diff should be computed from the merge commit or feature branch diff against the base branch. Keep the summary concise — file list with +/- counts, not full diffs.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6997ceab59e7a373079d88d3 |
| **Card Name** | Summary of changes added to the bean. |
| **Card URL** | https://trello.com/c/10AK7iyi/35-summary-of-changes-added-to-the-bean |

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
