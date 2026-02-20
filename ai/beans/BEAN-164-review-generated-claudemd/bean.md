# BEAN-164: Review and Prune Generated CLAUDE.md

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-164 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-02-20 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

When Foundry generates a new application, the CLAUDE.md file in the generated project includes references to sub-agents and personas that are not part of the selected team. For example, a project with team members [compliance-risk, integrator-merge-captain, research-librarian, team-lead, technical-writer] still has other agent types listed in the CLAUDE.md. The generated CLAUDE.md is too verbose and contains irrelevant content.

## Goal

Investigate how CLAUDE.md is generated, identify why non-selected personas appear, and fix the generation logic to only include team members that were actually selected. Prune the template/generation to produce a cleaner, more focused CLAUDE.md.

## Scope

### In Scope
- Investigate the CLAUDE.md generation pipeline (compiler service, templates)
- Identify why non-selected personas/agents appear in the output
- Fix the generation logic to filter CLAUDE.md content to only selected team members
- Ensure the generated CLAUDE.md is concise and relevant

### Out of Scope
- Redesigning the CLAUDE.md format entirely
- Modifying the Foundry project's own CLAUDE.md

## Acceptance Criteria

- [ ] Generated CLAUDE.md only references team members that were selected in the composition
- [ ] No extraneous persona/agent references appear for non-selected team members
- [ ] Generated CLAUDE.md is concise — no verbose boilerplate for unused features
- [ ] Existing test for CLAUDE.md generation is updated or new test added
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

Look at the generated project in `generated-projects/my-new-app-idea/` for a concrete example. The team was [compliance-risk, integrator-merge-captain, research-librarian, team-lead, technical-writer] but CLAUDE.md had other agent types listed.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 69984597908c4c734466f8be |
| **Card Name** | Review Claude.md |
| **Card URL** | https://trello.com/c/zLLmGx8X/38-review-claudemd |

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
