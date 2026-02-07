# Task 01: Create /deploy Command and Skill

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Status** | Done |
| **Depends On** | — |

## Goal

Create the `/deploy` command and skill that promotes `test` → `main` with a full quality gate.

## Inputs

- `ai/beans/BEAN-013-deploy-command/bean.md` — acceptance criteria and release notes format
- `.claude/commands/merge-bean.md` — pattern reference for command format
- `.claude/skills/merge-bean/SKILL.md` — pattern reference for skill format
- `.claude/agents/team-lead.md` — agent to update

## Implementation

1. **`.claude/commands/deploy.md`**: New command with usage, inputs, process (checkout test, run tests, code quality review, security review, generate release notes, present summary, wait for approval, merge to main, push), error handling, examples
2. **`.claude/skills/deploy/SKILL.md`**: New skill with phased process:
   - Phase 1: Preparation (checkout test, pull latest, verify clean state)
   - Phase 2: Quality Gate (run tests, code quality review, security review)
   - Phase 3: Release Notes (identify beans since last deploy, summarize)
   - Phase 4: User Approval (present everything, wait for "go")
   - Phase 5: Merge & Push (merge test → main with --no-ff, push, optional tag)
3. **`.claude/agents/team-lead.md`**: Add `/deploy` to Skills & Commands table

## Acceptance Criteria

- [ ] `/deploy` command created matching existing patterns
- [ ] `/deploy` skill created with phased process
- [ ] Quality gate includes tests, code quality review, security review
- [ ] Release notes generation documented
- [ ] User approval gate documented (explicit "go" required)
- [ ] Safe merge with `--no-ff` documented
- [ ] Team Lead agent updated
- [ ] Error handling covers common failure cases

## Definition of Done

Command, skill, and agent files created/updated.
