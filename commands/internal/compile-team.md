---
name: compile-team
description: "Assemble a unified CLAUDE.md file and supporting artifacts from the AI Team Library. The command reads a composition spec (which personas, stacks, and hooks were selected), resolves all references against the library, and produces a single compiled output that Claude Code can consume as its operating instructions for the project."
---

# /compile-team

This command is a thin entry point; the canonical process lives in the
`compile-team` skill — single source of truth (SPEC-023). The two used to be
maintained as parallel prose copies and drifted.

Read `.claude/skills/internal/compile-team/SKILL.md` and execute its process with these arguments:

$ARGUMENTS
