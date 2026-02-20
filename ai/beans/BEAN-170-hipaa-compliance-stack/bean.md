# BEAN-170: HIPAA Compliance Stack

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-170 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The ai-team-library has SOX and ISO 9000 compliance stacks but lacks HIPAA coverage. Teams building healthcare applications need guidance on PHI handling, the Privacy and Security Rules, BAAs, breach notification, and audit controls.

## Goal

Add a complete HIPAA compliance tech stack to the ai-team-library following the established stack template pattern.

## Scope

### In Scope
- HIPAA Privacy Rule and Security Rule guidance
- Administrative, physical, and technical safeguards
- Business associate agreements (BAAs)
- Breach notification procedures
- Audit controls for protected health information (PHI)
- Stack file following standardized template (Defaults, Do/Don't, Common Pitfalls, Checklist, code examples)

### Out of Scope
- Modifications to other compliance stacks
- Application code changes

## Acceptance Criteria

- [ ] `ai-team-library/stacks/hipaa-compliance/` directory exists with properly formatted stack file
- [ ] Stack file follows the standardized template pattern (Defaults table+alternatives, Do/Don't, Common Pitfalls, Checklist)
- [ ] Covers Privacy Rule, Security Rule, safeguards, BAAs, breach notification, and audit controls
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

Complements existing SOX and ISO 9000 compliance stacks.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998e29326f6fdd571a63bf1 |
| **Card Name** | HIPAA Compliance Stack |
| **Card URL** | https://trello.com/c/6913ABvW/48-hipaa-compliance-stack |

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
