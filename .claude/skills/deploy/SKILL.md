# Skill: Deploy

## Description

Promotes `test` to `main` via a pull request. Creates the PR, runs tests, and merges if they pass. One approval, no extra prompts.

## Trigger

- Invoked by the `/deploy` slash command.
- Requires `test` branch to exist and be ahead of `main`.

## Process

### Phase 1: Preparation

1. **Save current branch** — Record it so we can return at the end.
2. **Auto-stash if dirty** — If `git status --porcelain` shows changes, run `git stash --include-untracked -m "deploy-auto-stash"`. Do NOT ask — just stash and continue.
3. **Checkout test** — `git checkout test`.
4. **Push test** — `git push origin test` to ensure remote is up to date.
5. **Verify ahead of main** — `git log main..test --oneline`. If empty, report "Nothing to deploy", restore stash, return to original branch, exit.

### Phase 2: Quality Gate

6. **Run tests** — `uv run pytest` on the test branch.
   - If any fail: report failures, restore stash, return to original branch. Stop.
   - If all pass: record the count.

7. **Run ruff** — `uv run ruff check foundry_app/`. Record result.

### Phase 3: Build Release Notes

8. **Identify beans** — Parse `git log main..test --oneline` for `BEAN-NNN:` messages. Cross-reference with `ai/beans/_index.md` for titles.

9. **Count branches to clean** — List all `bean/*` branches (local + remote). Count how many are merged into test.

### Phase 4: User Approval — ONE prompt

10. **Present summary and ask once:**
    ```
    ===================================================
    DEPLOY: test → main (via PR)
    ===================================================

    Beans: <list>
    Tests: N passed, 0 failed
    Ruff: clean / N violations

    Post-merge: N feature branches will be deleted

    On "go": create PR, merge it, delete branches,
    restore working tree. No further prompts.
    ===================================================
    ```

11. **Single approval** with options: go / go with tag / abort.

    **CRITICAL: This is the ONLY user prompt. Everything after "go" runs without stopping.**

### Phase 5: Execute (no further prompts)

12. **Create PR:**
    ```bash
    gh pr create --base main --head test \
      --title "Deploy: <date> — <bean list summary>" \
      --body "<release notes>"
    ```

13. **Merge PR:**
    ```bash
    gh pr merge <pr-number> --merge --subject "Deploy: <date> — <bean list>"
    ```
    Use `--merge` (not squash/rebase) to preserve history.

14. **Tag (optional)** — If requested: `git tag <version> && git push origin --tags`.

15. **Delete local feature branches** — All `bean/*` branches merged into main: `git branch -d`. Stale/orphaned ones for Done beans: `git branch -D`.

16. **Delete remote feature branches** — Any `remotes/origin/bean/*`: `git push origin --delete`.

17. **Sync local main** — `git checkout main && git pull origin main`.

18. **Restore stash** — If we auto-stashed: `git stash pop`. On conflict, prefer HEAD for files that came from test.

19. **Report success** — PR URL, merge commit, beans deployed, branches deleted.

## Key Rules

- **One approval gate.** User says "go" once. Everything after is automatic.
- **Auto-stash, auto-restore.** Dirty working tree handled silently.
- **PR is created AND merged.** Not just created — the full cycle completes.
- **Branch cleanup included.** No separate step needed.
- **If a command is blocked by sandbox:** print the exact command for the user to run manually, then continue with the rest.

## Error Conditions

| Error | Resolution |
|-------|------------|
| Nothing to deploy | Report and exit |
| Tests fail | Report failures, restore stash, return. Fix first. |
| PR create fails | Report error. Check `gh auth status`. |
| PR merge fails | Report error. Check branch protection / conflicts. |
| User aborts | Restore stash, return to original branch |
| Command blocked | Print command for manual execution, continue |
