---
name: deploy
description: "Promotes code through the deployment pipeline using pull requests. Two modes: /deploy test merges the current branch into test (staging), and /deploy promotes test into main (production) with tagging and branch cleanup."
---

# /deploy

This command is a thin entry point; the canonical process lives in the
`deploy` skill — single source of truth (SPEC-023). The two used to be
maintained as parallel prose copies and drifted.

Read `.claude/skills/deploy/SKILL.md` and execute its process with these arguments:

$ARGUMENTS
