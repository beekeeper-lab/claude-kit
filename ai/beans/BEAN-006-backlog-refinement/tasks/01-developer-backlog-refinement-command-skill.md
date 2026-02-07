# Task 01: Create Backlog Refinement Command & Skill

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Status** | Done |
| **Depends On** | — |

## Goal

Create the `/backlog-refinement` command and skill files, and update the Team Lead agent to reference them.

## Inputs

- `ai/beans/BEAN-006-backlog-refinement/bean.md` — acceptance criteria and notes
- `.claude/commands/pick-bean.md` — reference command format
- `.claude/skills/pick-bean/SKILL.md` — reference skill format
- `.claude/skills/new-bean/SKILL.md` — referenced by this skill (creates beans)
- `.claude/agents/team-lead.md` — agent to update

## Implementation

1. Create `.claude/commands/backlog-refinement.md` with standard sections
2. Create `.claude/skills/backlog-refinement/SKILL.md` with standard sections
3. Update `.claude/agents/team-lead.md` to add `/backlog-refinement` to Skills & Commands table

### Key Skill Process

The skill should define an iterative, conversational flow:
1. Accept free-form text input from the user
2. Analyze the text — identify distinct units of work, themes, features
3. Present an initial breakdown to the user (proposed beans with titles)
4. Ask clarifying questions: scope boundaries, priorities, dependencies, missing context
5. Iterate with the user until agreement on the bean set
6. Create each bean via `/new-bean` with complete fields
7. Present a summary of all created beans

## Acceptance Criteria

- [ ] `.claude/commands/backlog-refinement.md` exists with all standard sections
- [ ] `.claude/skills/backlog-refinement/SKILL.md` exists with all standard sections
- [ ] Command accepts free-form text input
- [ ] Skill process includes clarifying questions phase
- [ ] Skill calls `/new-bean` to create each resulting bean
- [ ] Skill ensures each bean has Problem Statement, Goal, Scope, AC
- [ ] Format matches existing commands/skills
- [ ] Team Lead agent updated

## Definition of Done

All 3 files created/updated. Format matches existing commands and skills.
