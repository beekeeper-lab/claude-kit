# Task 02: Deploy Command Verification

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Status** | Done |
| **Depends On** | 01 |

## Goal

Verify the deploy command is complete, consistent, and well-documented.

## Inputs

- `ai/beans/BEAN-013-deploy-command/bean.md` — acceptance criteria
- `.claude/commands/deploy.md` — new command
- `.claude/skills/deploy/SKILL.md` — new skill
- `.claude/agents/team-lead.md` — updated agent

## Acceptance Criteria

- [ ] All bean acceptance criteria traced and met
- [ ] Quality gate is complete (tests + 2 reviews)
- [ ] User approval gate is clear (must say "go")
- [ ] Merge uses --no-ff
- [ ] No contradictions with existing branch workflow
- [ ] QA report written to `ai/outputs/tech-qa/bean-013-deploy-command-qa-report.md`

## Definition of Done

QA report exists with go/no-go recommendation.
