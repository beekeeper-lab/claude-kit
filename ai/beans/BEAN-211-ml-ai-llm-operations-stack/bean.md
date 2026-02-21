# BEAN-211: ML/AI & LLM Operations Stack

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-211 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 20:03 |
| **Completed** | 2026-02-20 20:10 |
| **Duration** | 7m |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a ml/ai & llm operations stack. Add mlops stack to ai-team-library. Model training pipelines, MLOps lifecycle, RAG patterns, prompt engineering conventions, model versioning, LLM integration patterns, feature stores, experiment tracking. Crosses business and technical domains.

## Goal

Add the stack to `ai-team-library/stacks/` with comprehensive, production-ready guidance.

## Scope

### In Scope
- Add mlops stack to ai-team-library. Model training pipelines, MLOps lifecycle, RAG patterns, prompt engineering conventions, model versioning, LLM integration patterns, feature stores, experiment tracking. Crosses business and technical domains.

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
| 1 | Create mlops conventions.md with defaults, do/don't, pitfalls, checklist | Developer | — | Done |
| 2 | Create model-training.md — training pipelines and experiment tracking | Developer | — | Done |
| 3 | Create llm-operations.md — LLM integration, RAG, prompt engineering | Developer | — | Done |
| 4 | Create feature-stores.md — feature management and serving | Developer | — | Done |
| 5 | Create model-versioning.md — model registry, versioning, deployment | Developer | — | Done |
| 6 | Update test_library_indexer.py EXPECTED_STACKS with "mlops" | Developer | 1 | Done |
| 7 | Run tests and lint — verify all pass | Tech-QA | 1-6 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #86.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f4c003ccc91849c37e25 |
| **Card Name** | ML/AI & LLM Operations Stack |
| **Card URL** | https://trello.com/c/ftkdW6nq |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create mlops conventions.md with defaults, do/don't, pitfalls, checklist | Developer | — | — | — | — |
| 2 | Create model-training.md — training pipelines and experiment tracking | Developer | — | — | — | — |
| 3 | Create llm-operations.md — LLM integration, RAG, prompt engineering | Developer | — | — | — | — |
| 4 | Create feature-stores.md — feature management and serving | Developer | — | — | — | — |
| 5 | Create model-versioning.md — model registry, versioning, deployment | Developer | — | — | — | — |
| 6 | Update test_library_indexer.py EXPECTED_STACKS with "mlops" | Developer | — | — | — | — |
| 7 | Run tests and lint — verify all pass | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 7 |
| **Total Duration** | 7m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |