---
name: review-pr
description: "Run a repeatable, checklist-driven code review covering readability, correctness, maintainability, convention consistency, test coverage, and security. Produces a clear verdict (ship / ship with comments / request changes) with actionable, line-level feedback. Optionally enforces green checks (tests + lint) as a gate before review begins."
---

# /review-pr

This command is a thin entry point; the canonical process lives in the
`review-pr` skill — single source of truth (SPEC-023). The two used to be
maintained as parallel prose copies and drifted.

Read `.claude/skills/internal/review-pr/SKILL.md` and execute its process with these arguments:

$ARGUMENTS
