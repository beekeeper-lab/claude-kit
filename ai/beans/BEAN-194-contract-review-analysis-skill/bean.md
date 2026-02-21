# BEAN-194: Contract Review & Analysis Skill

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-194 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 19:33 |
| **Completed** | 2026-02-20 19:37 |
| **Duration** | 4m |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a contract review & analysis skill. Add contract-review skill to ai-team-library. Reading and analyzing software contracts, SLAs, vendor agreements, MSAs. Identifying unfavorable clauses, liability caps, termination terms, and renewal traps.

## Goal

Add the content to the ai-team-library with comprehensive, actionable guidance.

## Scope

### In Scope
- Add contract-review skill to ai-team-library. Reading and analyzing software contracts, SLAs, vendor agreements, MSAs. Identifying unfavorable clauses, liability caps, termination terms, and renewal traps.

### Out of Scope
- Changes to the Foundry application code
- Modifications to existing library content

## Acceptance Criteria

- [x] Skill documentation created following library conventions
- [x] Covers all key topics described in the card description
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Create contract-review skill SKILL.md | Developer | — | Done |
| 2 | Verify tests pass and lint clean | Tech-QA | 1 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #69.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f3d5d5b5fbf6e6e39e2c |
| **Card Name** | Contract Review & Analysis Skill |
| **Card URL** | https://trello.com/c/2FrAna3H |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create contract-review skill SKILL.md | Developer | — | — | — | — |
| 2 | Verify tests pass and lint clean | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 4m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |