# BEAN-214: Add Category Metadata to All Persona Files

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-214 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-02-21 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The 24 persona files in ai-team-library lack category metadata. To support grouped display in the Foundry wizard UI, each persona.md needs a `## Category` section with one of four values: Software Development, Data & Analytics, Compliance & Legal, or Business Operations.

## Goal

Add a `## Category` section to all 24 persona.md files in `ai-team-library/personas/` with the correct category value. Update the test_library_indexer.py to validate that all personas have the expected category.

## Scope

### In Scope
- Add `## Category` section (after the existing metadata/header, before `## Mission`) to each persona.md
- Category assignments:
  - **Software Development**: architect, ba, code-quality-reviewer, developer, devops-release, integrator-merge-captain, mobile-developer, platform-sre-engineer, security-engineer, team-lead, tech-qa, technical-writer, ux-ui-designer
  - **Data & Analytics**: data-analyst, data-engineer, database-administrator
  - **Compliance & Legal**: compliance-risk, legal-counsel
  - **Business Operations**: change-management, customer-success, financial-operations, product-owner, sales-engineer, researcher-librarian
- Update test assertions to verify category values for all personas

### Out of Scope
- Changes to the PersonaInfo model (that's BEAN-213)
- UI changes (that's BEAN-215)
- Categorizing stacks or hook packs

## Acceptance Criteria

- [ ] All 24 persona.md files have a `## Category` section with one of the four category values
- [ ] Category section is consistently placed in all files (after header/metadata, before Mission)
- [ ] test_library_indexer.py includes assertions that each persona has the expected category
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

Depends on BEAN-213 (category field in PersonaInfo model) so the indexer can parse the new section. Can be developed in parallel if the parsing logic from BEAN-213 is known, but tests will only pass once both are merged.

Category assignments:
- Software Development (13): architect, ba, code-quality-reviewer, developer, devops-release, integrator-merge-captain, mobile-developer, platform-sre-engineer, security-engineer, team-lead, tech-qa, technical-writer, ux-ui-designer
- Data & Analytics (3): data-analyst, data-engineer, database-administrator
- Compliance & Legal (2): compliance-risk, legal-counsel
- Business Operations (6): change-management, customer-success, financial-operations, product-owner, sales-engineer, researcher-librarian

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
