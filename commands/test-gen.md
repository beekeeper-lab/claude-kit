---
name: test-gen
description: "Generate tests for the specified component or functionality using the project's own test stack — behavior-first coverage of the critical paths, then unit tests for uncovered logic."
argument-hint: <component or functionality>
---

# Test Generation (Behavior-First)

Generate tests for the specified target. Cover the **user-visible behavior
first** (the paths a user or caller actually exercises), then backfill unit
tests for uncovered logic and edge cases.

## Stack Detection (do this first)

This command is stack-neutral. Determine the project's real test stack —
never assume a framework:

1. Read `CLAUDE.md` for the documented test command and any testing
   conventions — they win.
2. Inspect existing tests (`tests/`, `__tests__/`, `*_test.go`,
   `src/**/*.test.*`) and MIRROR their style: fixtures, naming, assertion
   idioms, directory layout.
3. Infer the runner from manifests when nothing is documented:
   `pyproject.toml` → pytest, `package.json` → its test script,
   `go.mod` → `go test`, `Cargo.toml` → `cargo test`, `*.csproj` →
   `dotnet test`.
4. Only use browser/E2E tooling (e.g. Playwright) if the project already
   has it configured — never introduce a new test framework in a test-gen
   pass.

## Instructions

- Map the target's behaviors before writing anything: public entry points,
  happy paths, error paths, boundaries (empty, max, malformed input).
- Prioritize: (1) critical user-visible flows, (2) boundary/error handling,
  (3) pure-logic edge cases.
- Each test asserts BEHAVIOR (what the caller observes), not implementation
  details (which internals were called).
- Tests must be independent and deterministic: no shared mutable state, no
  ordering dependence, no real network/clock unless the project's existing
  tests do it.
- Run the discovered test command after generation and report the result —
  generated tests that don't run are worse than no tests.

## Output

1. New/updated test files following the project's existing layout.
2. A short coverage note: behaviors now covered, behaviors deliberately
   not covered and why.
3. The test-run result (command + pass/fail counts).

## Target

$ARGUMENTS
