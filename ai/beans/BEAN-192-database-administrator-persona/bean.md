# BEAN-192: Database Administrator Persona

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-192 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a database administrator persona. Add DBA persona to ai-team-library. Schema migrations, query optimization, backup strategies, replication. Drives the orphaned sql-dba stack.

## Goal

Add the persona to `ai-team-library/personas/` with complete persona definition, outputs, prompts, and templates.

## Scope

### In Scope
- Add DBA persona to ai-team-library. Schema migrations, query optimization, backup strategies, replication. Drives the orphaned sql-dba stack.

### Out of Scope
- Changes to the Foundry application code
- Modifications to existing library content

## Acceptance Criteria

- [ ] Persona directory created in `ai-team-library/personas/` with persona.md, outputs.md, prompts.md, templates/
- [ ] persona.md follows standardized format with mission, capabilities, boundaries
- [ ] outputs.md defines deliverable types and formats
- [ ] prompts.md provides reusable prompt templates
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

Sourced from Trello card #66.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f34ac495d932ded417b7 |
| **Card Name** | Database Administrator Persona |
| **Card URL** | https://trello.com/c/RpW59b2V |

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
