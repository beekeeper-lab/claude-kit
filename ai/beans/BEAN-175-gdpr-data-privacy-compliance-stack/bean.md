# BEAN-175: GDPR & Data Privacy Compliance Stack

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-175 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The ai-team-library has SOX and ISO 9000 compliance stacks but lacks GDPR/data privacy coverage. Teams building applications that handle EU personal data need guidance on data subject rights, privacy by design, DPIAs, cross-border transfers, and breach notification.

## Goal

Add a complete GDPR/data privacy compliance stack to the ai-team-library following the established stack template pattern.

## Scope

### In Scope
- GDPR fundamentals and key principles
- Data subject rights (access, erasure, portability, etc.)
- Privacy by design and by default
- Data protection impact assessments (DPIAs)
- Cross-border data transfers (SCCs, adequacy decisions)
- Breach notification procedures
- References to GDPR text, ICO guidance, and EDPB guidelines
- Stack file following standardized template

### Out of Scope
- Modifications to existing compliance stacks
- Country-specific implementations beyond GDPR
- Application code changes

## Acceptance Criteria

- [ ] `ai-team-library/stacks/gdpr-data-privacy/` directory exists with properly formatted stack file
- [ ] Stack file follows the standardized template pattern (Defaults table+alternatives, Do/Don't, Common Pitfalls, Checklist)
- [ ] Covers GDPR fundamentals, data subject rights, privacy by design, DPIAs, cross-border transfers, and breach notification
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

Follows the pattern of iso-9000 and sox-compliance stacks. References GDPR text, ICO guidance, and EDPB guidelines.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998e28ca32d2ac1d7ffdd53 |
| **Card Name** | GDPR & Data Privacy Compliance Stack |
| **Card URL** | https://trello.com/c/fGMVrtXp/44-gdpr-data-privacy-compliance-stack |

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
