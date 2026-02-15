# BEAN-128: Generation Progress UI — Missing Stages

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-128 |
| **Status** | Approved |
| **Priority** | Low |
| **Created** | 2026-02-15 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The generation progress screen (`generation_progress.py`) defines `PIPELINE_STAGES` with only 6 stages, but the actual generator pipeline runs 8 stages. The `agent_writer` and `mcp_config` stages are missing from the progress UI, so users don't see progress updates for agent file generation or MCP config writing. The progress bar and stage indicators skip directly from "Compile prompts" to "Copy assets," hiding two stages of work.

## Goal

The generation progress screen shows all 8 pipeline stages so users can see progress for every stage of generation including agent writing and MCP config.

## Scope

### In Scope
- Add `agent_writer` ("Write agent files") and `mcp_config` ("Write MCP config") to `PIPELINE_STAGES` in the correct positions
- Verify the stage IDs match what the generator emits

### Out of Scope
- Changing the progress screen layout or design
- Adding new pipeline stages

## Acceptance Criteria

- [ ] `PIPELINE_STAGES` lists all 8 stages in the correct order
- [ ] Stage IDs match the generator's stage identifiers
- [ ] Progress bar correctly advances through all 8 stages during generation
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Quick fix — add two entries to the `PIPELINE_STAGES` list
- Current order: scaffold, compile, copy_assets, seed_tasks, safety, diff_report
- Correct order: scaffold, compile, agent_writer, copy_assets, mcp_config, seed_tasks, safety, diff_report
- Related to BEAN-033 (Generation Progress Screen) which created the original UI

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
