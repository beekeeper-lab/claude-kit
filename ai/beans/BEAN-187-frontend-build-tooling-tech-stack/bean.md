# BEAN-187: Frontend Build & Tooling Tech Stack

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-187 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 19:19 |
| **Completed** | 2026-02-20 19:23 |
| **Duration** | 4m |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a frontend build & tooling tech stack. Add frontend tooling stack to ai-team-library. Vite, Webpack, monorepo tooling (Nx, Turborepo), bundling, tree-shaking, code splitting.

## Goal

Add the stack to `ai-team-library/stacks/` with comprehensive, production-ready guidance.

## Scope

### In Scope
- Add frontend tooling stack to ai-team-library. Vite, Webpack, monorepo tooling (Nx, Turborepo), bundling, tree-shaking, code splitting.

### Out of Scope
- Changes to the Foundry application code
- Modifications to existing library content

## Acceptance Criteria

- [x] Stack file created in `ai-team-library/stacks/` following standardized template
- [x] Includes: Defaults table with alternatives, Do/Don't lists, Common Pitfalls, Checklist, code examples
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Create bundlers stack file (Vite, Webpack, esbuild, Rollup) | Developer | — | Done |
| 2 | Create monorepo tooling stack file (Nx, Turborepo, workspaces) | Developer | — | Done |
| 3 | Verify acceptance criteria, run tests and lint | Tech-QA | 1, 2 | Done |

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #60.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f341d66a14c10cc26fcf |
| **Card Name** | Frontend Build & Tooling Tech Stack |
| **Card URL** | https://trello.com/c/t9XymyxA |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create bundlers stack file (Vite, Webpack, esbuild, Rollup) | Developer | — | — | — | — |
| 2 | Create monorepo tooling stack file (Nx, Turborepo, workspaces) | Developer | — | — | — | — |
| 3 | Verify acceptance criteria, run tests and lint | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 3 |
| **Total Duration** | 4m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |