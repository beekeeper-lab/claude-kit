# BEAN-171: Rust Language Tech Stack

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-171 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The ai-team-library has language stacks for Python, Java, Node, and TypeScript but lacks Rust coverage. Rust's unique memory model (ownership/borrowing) requires specific guidance not found in other language stacks.

## Goal

Add a complete Rust language tech stack to the ai-team-library following the established stack template pattern.

## Scope

### In Scope
- Ownership and borrowing conventions
- Error handling patterns (Result, Option, custom errors)
- Unsafe code guidelines
- Concurrency patterns (async/await, channels, Arc/Mutex)
- Performance optimization guidance
- Testing strategies (unit, integration, property-based)
- Stack file following standardized template

### Out of Scope
- Modifications to other language stacks
- Application code changes

## Acceptance Criteria

- [ ] `ai-team-library/stacks/rust/` directory exists with properly formatted stack file
- [ ] Stack file follows the standardized template pattern (Defaults table+alternatives, Do/Don't, Common Pitfalls, Checklist)
- [ ] Covers ownership/borrowing, error handling, unsafe code, concurrency, performance, and testing
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

Rust is the dominant language for systems programming and WebAssembly targets.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998e29467458485504c2671 |
| **Card Name** | Rust Language Tech Stack |
| **Card URL** | https://trello.com/c/1rsDgy14/49-rust-language-tech-stack |

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
