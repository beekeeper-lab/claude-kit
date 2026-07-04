---
name: trello-load
description: "Connects to Trello via the MCP server, pulls all cards from a board's Sprint_Backlog list, and creates well-formed beans directly from each card's content. Beans are created with Approved status. After each bean is created, the source card is moved to In_Progress on Trello."
---

# /trello-load

This command is a thin entry point; the canonical process lives in the
`trello-load` skill — single source of truth (SPEC-023). The two used to be
maintained as parallel prose copies and drifted.

Read `.claude/skills/internal/trello-load/SKILL.md` and execute its process with these arguments:

$ARGUMENTS
