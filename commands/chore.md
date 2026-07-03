---
name: chore
description: "Create a chore plan in specs/*.md (refactor, upgrade, cleanup) with behavior-preservation checks. Detects the project's stack and test runner instead of assuming one."
argument-hint: <chore description>
---

# Chore Planning

Create a new plan in `specs/*.md` for the `Chore` using the exact
`Plan Format` below. Chores change structure, not behavior — the plan's
job is proving behavior is preserved.

## Stack Detection (do this first)

This command is stack-neutral. Determine the project's real tooling before
planning — never assume a framework:

1. Read `CLAUDE.md` for documented test/lint/build commands — they win.
2. Otherwise infer from manifests: `pyproject.toml`, `package.json`,
   `go.mod`, `Cargo.toml`, `*.csproj`.
3. Record the discovered commands in the plan's Validation Commands section.

## Instructions

- Create the plan in `specs/*.md`, named after the `Chore`.
- Capture the baseline FIRST: run the full test suite before any change and
  record the passing count — that number must not drop.
- For chores that affect user-visible surfaces (UI refactors, dependency
  upgrades), include a manual or scripted smoke-check of the affected
  surface using the project's own tooling.
- IMPORTANT: Replace every <placeholder> in the `Plan Format` with the requested value.
- Keep mechanical steps (renames, moves) separate from judgment steps
  (API changes) so each commit is reviewable.

## Plan Format

```markdown
# Chore: <chore name>

## Description
<what is being cleaned up / upgraded / restructured, and why now>

## Behavior Preservation Contract
<what must NOT change; baseline test count from the pre-change run>

## Steps
<numbered steps; mechanical vs judgment steps separated>

## Relevant Files
<files touched, one line each with why>

## Validation Commands
- `<discovered test command>` — same-or-better pass count vs baseline
- `<discovered lint command>` — lint clean
- <surface smoke-check when user-visible areas are touched>

## Notes
<optional: risks, rollback plan, follow-ups>
```

## Chore

$ARGUMENTS
