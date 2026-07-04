---
name: validate-config
description: "Catch hardcoded secrets, missing config variables, untracked .env files, and cross-environment inconsistencies before they cause outages or security incidents. This is the config equivalent of running a linter -- it catches the common mistakes that break deployments and leak credentials."
---

# /validate-config

This command is a thin entry point; the canonical process lives in the
`validate-config` skill — single source of truth (SPEC-023). The two used to be
maintained as parallel prose copies and drifted.

Read `.claude/skills/internal/validate-config/SKILL.md` and execute its process with these arguments:

$ARGUMENTS
