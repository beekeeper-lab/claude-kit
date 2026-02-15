# BEAN-124: Hook-Selective Asset Copier

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-124 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-02-15 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The asset copier currently copies ALL hook files from the library into generated projects, regardless of which hook packs the user selected in the wizard. If a user only picks "pre-commit-lint" and "git-commit-branch," they still get all 12 hook markdown files including Azure DevOps and compliance hooks they don't need. Commands and skills should continue copying wholesale, but hooks should respect the user's wizard selections.

## Goal

When generation completes, only the hook files corresponding to the hook packs selected in the wizard are present in the output `.claude/hooks/` directory. Commands and skills continue to be copied in full from the library.

## Scope

### In Scope
- Modify `asset_copier.py` to filter hook files based on `spec.hooks` selections
- Map hook pack IDs from the composition spec to specific hook files in the library
- Maintain full copy behavior for commands and skills (no filtering)
- Update tests to verify selective hook copying

### Out of Scope
- Filtering commands or skills by persona
- Adding a wizard page for explicit hook file selection (packs are sufficient)
- Changing the hook file format or content

## Acceptance Criteria

- [ ] Only hook files matching the selected hook packs are copied to the output
- [ ] If no hook packs are selected, no hook files are copied
- [ ] Commands and skills are still copied in full regardless of selections
- [ ] Existing asset copier tests updated to cover selective behavior
- [ ] New tests verify hook filtering with various pack combinations
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- The hook packs are defined in `ai-team-library/claude/hooks/` — each markdown file is a hook definition
- The composition spec's `hooks` field contains the selected hook pack references
- Related to BEAN-069 (Workflow Hook Packs) which originally created the hook system

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
