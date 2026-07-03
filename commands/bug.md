---
name: bug
description: "Create a TDD bug-fix plan in specs/*.md: reproduce the bug with a failing test, fix it, keep the test as a regression guard. Detects the project's stack and test runner instead of assuming one."
argument-hint: <bug description>
---

# Bug Planning (TDD Approach)

Create a new plan in `specs/*.md` to resolve the `Bug` using the exact
`Plan Format` below and **Test-Driven Development** principles.

## Stack Detection (do this first)

This command is stack-neutral. Before writing the plan, determine the
project's real tooling — never assume a framework:

1. Read `CLAUDE.md` for documented test/lint/build commands — they win.
2. Otherwise infer from manifests: `pyproject.toml` (pytest/ruff, likely
   `uv run`), `package.json` scripts (vitest/jest/playwright), `go.mod`
   (`go test ./...`), `Cargo.toml` (`cargo test`), `*.csproj`
   (`dotnet test`), etc.
3. Record the discovered commands in the plan's Validation Commands
   section. If no test runner exists, say so in the plan and propose the
   conventional one for the stack.

## Instructions

- You're writing a plan to fix a bug using **TDD**.
- Create the plan in `specs/*.md`, named after the `Bug`.
- Research the codebase to understand the bug, reproduce it, and plan the fix.
- IMPORTANT: Replace every <placeholder> in the `Plan Format` with the requested value.
- THINK HARD about the root cause and how to prevent regression.

### TDD for Bug Fixes

1. **Write a failing test that reproduces the bug** — proves the bug exists.
2. **Fix the bug** — make the test pass.
3. **The test becomes a regression test** — the bug can never return undetected.

Choose the smallest test type that reproduces the bug: unit test for
logic/data bugs, integration test for boundary bugs, end-to-end test only
when the bug is genuinely in the assembled system (use the project's E2E
tooling if it has one).

## Plan Format

```markdown
# Bug: <bug name>

## Bug Description
<detailed description of the bug>

## Problem Statement
<clearly define the problem>

## Reproduction Steps
<numbered steps that reproduce the bug today>

## Root Cause
<the actual cause, with file:line references>

## Failing Test (write FIRST)
<test file path and the test that reproduces the bug>

## Fix
<numbered implementation steps, smallest change that makes the test pass>

## Relevant Files
<files to read/modify, one line each with why>

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.
- `<discovered test command>` — full suite passes
- `<discovered lint command>` — lint clean
- <any bug-specific verification>

## Notes
<optional: gotchas, follow-ups, related issues>
```

## Bug

$ARGUMENTS
