# Skill: Deploy

## Description

Promotes the `test` integration branch to `main` with a full quality gate. Runs tests, performs code quality and security reviews, generates release notes listing all included beans, and waits for explicit user approval before merging. This is the only authorized path for getting code onto `main`.

## Trigger

- Invoked by the `/deploy` slash command.
- Should only be used by the Team Lead persona.
- Requires `test` branch to exist and be ahead of `main`.

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| tag | String | No | Version tag for the merge commit (e.g., `v1.2.0`) |
| test_branch | Git branch | Yes | The `test` integration branch |
| main_branch | Git branch | Yes | The `main` production branch |
| bean_index | Markdown file | Yes | `ai/beans/_index.md` for release notes |

## Process

### Phase 1: Preparation

1. **Checkout test** — `git checkout test`.
2. **Pull latest** — `git pull origin test`.
3. **Verify ahead of main** — Run `git log main..test --oneline`. If empty, report "Nothing to deploy — test is not ahead of main" and exit.
4. **Check clean state** — Ensure no uncommitted changes: `git status --porcelain`. If dirty, report and exit.

### Phase 2: Quality Gate

5. **Run test suite** — Execute `uv run pytest` on the `test` branch.
   - If any tests fail: report the failures. Do not proceed. The user should fix issues on a bean branch first.
   - If all pass: record the count (e.g., "300 passed, 0 failed").

6. **Code quality review** — Acting as the **code-quality-reviewer** persona:
   - Run `git diff main..test` to see all changes being deployed.
   - Review for: code style, patterns, complexity, maintainability, dead code, naming consistency.
   - Write report to `ai/outputs/code-quality-reviewer/deploy-YYYY-MM-DD.md`.
   - Verdict: PASS or FAIL with specific findings.

7. **Security review** — Acting as the **security-engineer** persona:
   - Review the same diff for: injection vulnerabilities, secrets exposure, OWASP top 10, unsafe patterns, dependency concerns.
   - Write report to `ai/outputs/security-engineer/deploy-YYYY-MM-DD.md`.
   - Verdict: PASS or FAIL with specific findings.

8. **Evaluate gate** — If either review is FAIL:
   - Present the findings to the user.
   - Ask if they want to proceed anyway or abort.
   - A FAIL does not automatically block — the user decides.

### Phase 3: Release Notes

9. **Identify beans** — Parse `git log main..test --oneline` to find commit messages matching `BEAN-NNN:`. Cross-reference with `ai/beans/_index.md` to get bean titles.

10. **Summarize changes** — For each bean:
    - Title and bean ID
    - 1-line summary of what changed
    - Key files affected (from the commits)

11. **Generate summary** — Produce a 2-3 sentence high-level overview of the release.

### Phase 4: User Approval

12. **Present summary** — Display to the user:
    ```
    ===================================================
    DEPLOY: test → main
    ===================================================

    Beans included:
      - BEAN-NNN: <title>
      - BEAN-NNN: <title>

    Reviews:
      Code Quality: PASS/FAIL
      Security: PASS/FAIL
      Tests: N passed, N failed

    Summary:
      <2-3 sentence overview>

    Proceed with merge to main? [go / abort]
    ===================================================
    ```

13. **Wait for approval** — The user must explicitly say "go" to proceed.
    - If "go": continue to Phase 5.
    - If "abort" or anything else: report "Deploy aborted by user" and return to previous branch.

### Phase 5: Merge & Push

14. **Checkout main** — `git checkout main`.
15. **Pull latest** — `git pull origin main`.
16. **Merge test** — `git merge test --no-ff -m "Deploy: <date> — <bean list>"`.
    - If merge conflict (shouldn't happen): abort, report, return to test.
17. **Tag (optional)** — If `tag` input was provided: `git tag <version>`.
18. **Push** — `git push origin main`. If tagged: `git push origin --tags`.
19. **Report success** — Output: merge commit hash, beans deployed, tag (if any), link to reports.

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| quality_report | Markdown file | `ai/outputs/code-quality-reviewer/deploy-YYYY-MM-DD.md` |
| security_report | Markdown file | `ai/outputs/security-engineer/deploy-YYYY-MM-DD.md` |
| release_notes | Console text | Summary of beans and changes being deployed |
| merge_commit | Git commit | Merge commit on `main` |
| version_tag | Git tag | Optional version tag |

## Quality Criteria

- Tests must pass before any merge is attempted.
- Both reviews (code quality + security) produce written reports.
- User must explicitly approve — no silent merges.
- Merge uses `--no-ff` to preserve history.
- The deploy is atomic: all of test goes to main, not cherry-picked commits.

## Error Conditions

| Error | Cause | Resolution |
|-------|-------|------------|
| `NothingToDeploy` | `test` is not ahead of `main` | Report and exit — no action needed |
| `DirtyWorkingTree` | Uncommitted changes exist | Commit or stash before deploying |
| `TestFailure` | Tests fail on `test` branch | Fix on a bean branch, merge to test, retry |
| `QualityGateFail` | Review finds blockers | User decides: proceed or abort |
| `MergeConflict` | Conflict merging test → main | Abort merge, report files. Shouldn't happen normally. |
| `UserDeclined` | User doesn't say "go" | Abort cleanly, no changes made |
| `PushFailure` | Push to main rejected | Report error for manual resolution |

## Dependencies

- `test` branch must exist with commits ahead of `main`
- `ai/beans/_index.md` for release notes generation
- Git repository in a clean state
- Push permissions for `main` (deploy is the only authorized path to main)
