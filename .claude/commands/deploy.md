# /deploy Command

Claude Code slash command that promotes the `test` integration branch to `main` with a full quality gate: tests, code quality review, security review, release notes, and user approval.

## Purpose

After beans are completed and merged to `test`, this command provides a deliberate, gated process for promoting that work to `main`. The user controls when deploys happen — they are never automatic.

## Usage

```
/deploy [--tag <version>]
```

- `--tag <version>` -- Optional. Tag the merge commit on `main` with a version (e.g., `v1.1.0`).

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| `test` branch | Git | Yes (must exist and have commits ahead of `main`) |
| `main` branch | Git | Yes (target for merge) |
| Bean index | `ai/beans/_index.md` | Yes (for release notes generation) |

## Process

1. **Checkout test** — `git checkout test && git pull origin test`.
2. **Verify ahead of main** — Check that `test` has commits not in `main`. If test is not ahead, report "Nothing to deploy" and stop.
3. **Run tests** — Execute `uv run pytest`. All tests must pass.
4. **Code quality review** — Acting as the code-quality-reviewer persona, review the diff between `main` and `test`. Produce a report at `ai/outputs/code-quality-reviewer/deploy-YYYY-MM-DD.md`.
5. **Security review** — Acting as the security-engineer persona, review the diff for vulnerabilities. Produce a report at `ai/outputs/security-engineer/deploy-YYYY-MM-DD.md`.
6. **Generate release notes** — Identify all beans merged to `test` since the last deploy. Produce a summary listing each bean's title and key changes.
7. **Present summary** — Show the user: release notes, review verdicts, test results.
8. **Wait for approval** — Ask the user for explicit "go" before proceeding. If the user declines, abort cleanly.
9. **Merge to main** — `git checkout main && git pull origin main && git merge test --no-ff`.
10. **Tag (optional)** — If `--tag` was provided: `git tag <version>`.
11. **Push** — `git push origin main` (and `git push origin --tags` if tagged).
12. **Report** — Output: merge commit hash, beans included, tag (if any).

## Output

| Artifact | Path | Description |
|----------|------|-------------|
| Code quality report | `ai/outputs/code-quality-reviewer/deploy-YYYY-MM-DD.md` | Quality review of test→main diff |
| Security report | `ai/outputs/security-engineer/deploy-YYYY-MM-DD.md` | Security review of test→main diff |
| Release notes | Console output | Summary of beans and changes being deployed |
| Merge commit | Git history on `main` | test merged into main |

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `NothingToDeploy` | `test` is not ahead of `main` | Report and stop — no action needed |
| `TestFailure` | Tests fail on `test` branch | Report failures; do not merge. Fix on a bean branch first. |
| `QualityGateFail` | Code quality or security review finds blockers | Report issues; do not merge. User decides whether to proceed. |
| `MergeConflict` | Conflict merging test → main | Report conflicting files; abort merge. This shouldn't happen if main is only updated via /deploy. |
| `UserDeclined` | User says "no" at approval gate | Abort cleanly, return to previous branch |
| `PushFailure` | Push to main fails | Report error for manual resolution |

## Examples

**Standard deploy:**
```
/deploy
```
Checks out test, runs tests, performs reviews, generates release notes, asks for approval, merges to main.

**Deploy with version tag:**
```
/deploy --tag v1.2.0
```
Same as above, plus tags the merge commit as `v1.2.0`.

**Typical approval prompt:**
```
===================================================
DEPLOY: test → main
===================================================

Beans included:
  - BEAN-012: Enforce Feature Branch Workflow
  - BEAN-013: Deploy Command
  - BEAN-014: Team Lead Progress Dashboard

Reviews:
  Code Quality: PASS
  Security: PASS
  Tests: 300 passed, 0 failed

Proceed with merge to main? [go / abort]
```
