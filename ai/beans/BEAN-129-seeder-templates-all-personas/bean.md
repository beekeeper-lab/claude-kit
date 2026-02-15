# BEAN-129: Seeder Templates for All Personas

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-129 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-02-15 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The seeder service (`seeder.py`) has hardcoded task templates for only 5 of 13 available personas: `team-lead`, `ba`, `architect`, `developer`, and `tech-qa`. When a user selects any of the other 8 personas (`code-quality-reviewer`, `devops-release`, `security-engineer`, `compliance-risk`, `researcher-librarian`, `technical-writer`, `ux-ui-designer`, `integrator-merge-captain`) with seed tasks enabled, the seeder logs a warning and produces no starter tasks for those personas. This means generated projects with specialized teams start with an incomplete task list.

## Goal

Every persona in the library has seed task templates in the seeder so that any team composition gets a complete starter task list covering all selected personas.

## Scope

### In Scope
- Add seed task templates for the 8 missing personas:
  - `code-quality-reviewer`
  - `devops-release`
  - `security-engineer`
  - `compliance-risk`
  - `researcher-librarian`
  - `technical-writer`
  - `ux-ui-designer`
  - `integrator-merge-captain`
- Each persona should get 2-4 starter tasks appropriate to their role
- Update seeder tests to verify all 13 personas produce tasks

### Out of Scope
- Changing the seeder's architecture or task format
- Making seed tasks configurable per-persona in the wizard
- Modifying existing seed task templates for the 5 personas that already have them

## Acceptance Criteria

- [ ] All 13 personas have seed task templates in the seeder
- [ ] Each new persona has at least 2 meaningful starter tasks
- [ ] No "No seed task templates" warnings are emitted for any library persona
- [ ] Seeder tests cover all 13 personas
- [ ] Generated `ai/tasks/_index.md` includes tasks for all selected personas
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Reference each persona's `persona.md` file in `ai-team-library/personas/<id>/` for role description and mission to derive appropriate starter tasks
- Related to BEAN-029 (Seeder Service) which created the original seeder with the 5 persona templates

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
