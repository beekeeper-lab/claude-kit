# BEAN-219: Add Category Metadata to All Expertise Files

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-219 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-02-21 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The 39 expertise items in ai-team-library lack category metadata. To support grouped display in the Foundry wizard UI, each expertise item needs a `## Category` section in its primary file with one of six category values.

## Goal

Add a `## Category` section to the primary markdown file in each of the 39 expertise directories in `ai-team-library/expertise/` with the correct category value. Update test assertions to validate categories.

## Scope

### In Scope
- Add `## Category` section to the first/primary .md file in each expertise directory
- Category assignments:
  - **Languages** (12): dotnet, go, java, kotlin, node, python, python-qt-pyside6, react, react-native, rust, swift, typescript
  - **Architecture & Patterns** (5): api-design, clean-code, event-driven-messaging, frontend-build-tooling, microservices
  - **Infrastructure & Platforms** (6): aws-cloud-platform, azure-cloud-platform, devops, gcp-cloud-platform, kubernetes, terraform
  - **Data & ML** (4): business-intelligence, data-engineering, mlops, sql-dba
  - **Compliance & Governance** (7): accessibility-compliance, gdpr-data-privacy, hipaa-compliance, iso-9000, pci-dss-compliance, security, sox-compliance
  - **Business Practices** (5): change-management, customer-enablement, finops, product-strategy, sales-engineering
- Update test_library_indexer.py to verify category for each expertise item

### Out of Scope
- Changes to the ExpertiseInfo model (that's BEAN-218)
- UI changes (that's BEAN-220)
- Persona categories (those are BEAN-213-215)

## Acceptance Criteria

- [ ] All 39 expertise items have a `## Category` section with one of the six category values
- [ ] Category section is consistently placed in the primary file of each expertise directory
- [ ] test_library_indexer.py includes assertions verifying each expertise item's category
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

Depends on BEAN-218 (category field in ExpertiseInfo) so the indexer can parse the new section.

Category assignments (39 items across 6 categories):
- Languages (12): dotnet, go, java, kotlin, node, python, python-qt-pyside6, react, react-native, rust, swift, typescript
- Architecture & Patterns (5): api-design, clean-code, event-driven-messaging, frontend-build-tooling, microservices
- Infrastructure & Platforms (6): aws-cloud-platform, azure-cloud-platform, devops, gcp-cloud-platform, kubernetes, terraform
- Data & ML (4): business-intelligence, data-engineering, mlops, sql-dba
- Compliance & Governance (7): accessibility-compliance, gdpr-data-privacy, hipaa-compliance, iso-9000, pci-dss-compliance, security, sox-compliance
- Business Practices (5): change-management, customer-enablement, finops, product-strategy, sales-engineering

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
