# BEAN-173: React Native Mobile Tech Stack

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-173 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The ai-team-library has React and TypeScript stacks but no mobile-specific guidance. React Native requires specific patterns for navigation, native module integration, performance optimization, and mobile testing that differ from web React.

## Goal

Add a complete React Native mobile tech stack to the ai-team-library following the established stack template pattern.

## Scope

### In Scope
- React Native conventions and project structure
- Navigation patterns (React Navigation)
- Native module integration
- Performance optimization (FlatList, memoization, bridge overhead)
- Mobile testing strategies (Jest, Detox, device testing)
- Stack file following standardized template

### Out of Scope
- Modifications to existing React or TypeScript stacks
- Flutter or other mobile frameworks
- Application code changes

## Acceptance Criteria

- [ ] `ai-team-library/stacks/react-native/` directory exists with properly formatted stack file
- [ ] Stack file follows the standardized template pattern (Defaults table+alternatives, Do/Don't, Common Pitfalls, Checklist)
- [ ] Covers conventions, navigation, native modules, performance, and testing
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

Natural extension of existing React and TypeScript stacks into mobile.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998e290abfb2c36b0d70da8 |
| **Card Name** | React Native Mobile Tech Stack |
| **Card URL** | https://trello.com/c/WZmx2VDh/46-react-native-mobile-tech-stack |

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
