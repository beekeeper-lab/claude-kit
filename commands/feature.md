---
name: feature
description: "Create a TDD feature plan in specs/*.md: tests define the behavior first, implementation makes them pass. Detects the project's stack and test runner instead of assuming one."
argument-hint: <feature description>
---

# Feature Planning (TDD Approach)

Create a new plan in `specs/*.md` to implement the `Feature` using the
exact `Plan Format` below and **Test-Driven Development** principles.

## Stack Detection (do this first)

This command is stack-neutral. Before writing the plan, determine the
project's real tooling — never assume a framework:

1. Read `CLAUDE.md` for documented test/lint/build commands — they win.
2. Otherwise infer from manifests: `pyproject.toml` (pytest/ruff, likely
   `uv run`), `package.json` scripts, `go.mod`, `Cargo.toml`, `*.csproj`.
3. Record the discovered commands in the plan's Validation Commands section.

## Instructions

- You're writing a plan to implement a feature using **TDD**: write the
  tests that define the behavior first, then implement until they pass.
- Create the plan in `specs/*.md`, named after the `Feature`.
- Research the codebase so the plan follows existing conventions, module
  boundaries, and naming.
- IMPORTANT: Replace every <placeholder> in the `Plan Format` with the requested value.
- Keep the slice thin: smallest end-to-end useful behavior first; note
  follow-on slices instead of inflating scope.

### Test layering

- Unit tests for logic and edge cases (fast, most of the pyramid).
- Integration tests where the feature crosses a boundary (API, DB, file system).
- End-to-end/UI tests only for the critical user-visible path, using
  whatever E2E tooling the project already has.

## Plan Format

```markdown
# Feature: <feature name>

## Description
<what the feature does and for whom>

## User Story
As a <user type>, I want <capability> so that <benefit>.

## Acceptance Criteria
<checkbox list; make each machine-verifiable where possible>

## Tests First
<test files and named test cases that define the behavior, written before implementation>

## Implementation Steps
<numbered steps; each step small enough to keep tests green at the end>

## Relevant Files
<files to create/modify, one line each with why>

## Validation Commands
- `<discovered test command>` — full suite passes, new tests included
- `<discovered lint command>` — lint clean
- <any feature-specific verification (e.g. run the app and exercise the flow)>

## Notes
<optional: out-of-scope items, follow-on slices, risks>
```

## Feature

$ARGUMENTS
