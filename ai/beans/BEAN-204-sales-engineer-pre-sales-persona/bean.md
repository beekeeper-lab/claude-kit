# BEAN-204: Sales Engineer / Pre-Sales Persona

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-204 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 19:49 |
| **Completed** | 2026-02-20 19:55 |
| **Duration** | 6m |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a sales engineer / pre-sales persona. Add sales-engineer persona to ai-team-library. Technical demos and POC builds, RFP/RFI responses, competitive analysis, technical win criteria, customer-facing architecture reviews. Pairs with Sales Engineering stack.

## Goal

Add the persona to `ai-team-library/personas/` with complete persona definition, outputs, prompts, and templates.

## Scope

### In Scope
- Add sales-engineer persona to ai-team-library. Technical demos and POC builds, RFP/RFI responses, competitive analysis, technical win criteria, customer-facing architecture reviews. Pairs with Sales Engineering stack.

### Out of Scope
- Changes to the Foundry application code
- Modifications to existing library content

## Acceptance Criteria

- [x] Persona directory created in `ai-team-library/personas/` with persona.md, outputs.md, prompts.md, templates/
- [x] persona.md follows standardized format with mission, capabilities, boundaries
- [x] outputs.md defines deliverable types and formats
- [x] prompts.md provides reusable prompt templates
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Create persona.md, outputs.md, prompts.md, templates/ | Developer | — | Done |
| 2 | Update test_library_indexer.py EXPECTED_PERSONAS | Developer | 1 | Done |
| 3 | Run tests and lint, verify acceptance criteria | Tech-QA | 2 | Done |

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #79.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f4b7fc90e1de95019824 |
| **Card Name** | Sales Engineer / Pre-Sales Persona |
| **Card URL** | https://trello.com/c/6Bwway12 |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create persona.md, outputs.md, prompts.md, templates/ | Developer | — | — | — | — |
| 2 | Update test_library_indexer.py EXPECTED_PERSONAS | Developer | — | — | — | — |
| 3 | Run tests and lint, verify acceptance criteria | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 3 |
| **Total Duration** | 6m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |