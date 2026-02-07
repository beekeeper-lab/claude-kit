# Task 01: Update Push Hooks, Settings, and Agent Files

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Status** | Done |
| **Depends On** | — |

## Goal

Refine push permissions to allow pushes to feature branches and integration branches while blocking pushes to protected branches (main/master).

## Inputs

- `ai/beans/BEAN-009-push-hook-refinement/bean.md` — acceptance criteria
- `.claude/settings.local.json` — current permissions
- `.claude/hooks/hook-policy.md` — current hook policy
- `.claude/agents/` — agent files to update

## Implementation

1. **`.claude/settings.local.json`**: Add deny rules for protected branches:
   - `Bash(git push origin main)`, `Bash(git push origin master)`
   - `Bash(git push * main)`, `Bash(git push * master)` (catch non-origin remotes)
   - Keep broad `Bash(git push *)` in allow (deny takes precedence)

2. **`.claude/hooks/hook-policy.md`**: Add a "Branch Protection" section documenting:
   - Protected branches: `main`, `master`
   - Allowed branch patterns: `bean/*`, `test`, `dev`
   - Push rules: feature/integration branches allowed, protected branches blocked
   - Force push always blocked (existing rule)

3. **Agent files**: Update relevant agents with push permission awareness:
   - Team Lead: note about branch protection in Operating Principles or Rules
   - Developer: awareness of which branches to push to

## Acceptance Criteria

- [ ] `settings.local.json` denies pushes to main/master
- [ ] `settings.local.json` allows pushes to bean/* branches
- [ ] Hook policy documents branch protection rules
- [ ] Agent files reflect push permission awareness
- [ ] No contradictions with existing settings

## Definition of Done

All files updated. Branch protection policy is clear and enforceable.
