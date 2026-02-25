# Skill: Deploy

## Description

Promotes code through the deployment pipeline using pull requests. Two modes:

- `/deploy test` — Merge the current feature branch into `test` (staging) via a GitHub PR.
- `/deploy` — Promote `test` into `main` (production) via a GitHub PR, tag the release, and clean up branches.

All merges use `gh pr create` + `gh pr merge` for traceability. One approval prompt per deploy. No extra prompts after "go".

## Trigger

- Invoked by the `/deploy` slash command.
- `/deploy test` can be run from any feature branch.
- `/deploy` (no args) must be run when `test` is ahead of `main`.

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| mode | String | No | `test` to deploy current branch → test. Omit to promote test → main. |
| tag | String | No | Version tag for production release (e.g., `v1.2.0`). Only used in production mode. If not provided, a date-based tag `deploy/YYYY-MM-DD` is used (appending `-2`, `-3`, etc. on collision). |

---

## Process — Mode A: `/deploy test` (branch → test)

### Phase 1: Preparation

1. **Record current branch** — `git branch --show-current`. If on `test` or `main`, report error: "Cannot deploy `test` or `main` to test — switch to a feature branch first." Exit.
2. **Check for uncommitted changes** — Run `git status --porcelain`.
   - If clean: continue.
   - If dirty: show modified/untracked files and prompt:
     - **Commit** — Stage all changes and commit with a descriptive message. Then continue.
     - **Stash** — Run `git stash --include-untracked -m "deploy-auto-stash"`. Restore at the end.
     - **Abort** — Stop the deploy.
3. **Push current branch** — `git push origin <branch> -u` to ensure the remote has the latest commits.

### Phase 2: Quality Gate

4. **Run tests** — `uv run pytest`.
   - If any fail: report failures, restore stash if applicable, stop.
5. **Run ruff** — `uv run ruff check foundry_app/`.
   - If violations: report, restore stash, stop.

### Phase 3: Create and Merge PR

6. **Create PR to test** — `gh pr create --base test --head <branch> --title "<branch>: merge to test" --body "Automated deploy to test via /deploy test"`.
   - If a PR already exists for this branch→test, use the existing one.
7. **Merge the PR** — `gh pr merge <pr-number> --merge`.
   - Use `--merge` (not squash or rebase) to preserve commit history.
   - Do NOT delete the source branch — it may still be in use.
8. **Sync local test** — `git fetch origin && git checkout test && git pull origin test`.
9. **Return to original branch** — `git checkout <original-branch>`.
10. **Restore stash** — If the user chose "Stash" in step 2: `git stash pop`.

### Phase 4: Status Check

11. **Run `/git-status`** — Show the current sync state of all branches. This confirms the merge landed and shows the pipeline status.

---

## Process — Mode B: `/deploy` (test → main)

### Phase 1: Preparation

1. **Save current branch** — Record it so we can return at the end.
2. **Check for uncommitted changes** — Run `git status --porcelain`.
   - If clean: continue.
   - If dirty: show modified/untracked files and prompt:
     - **Commit** — Stage all changes and commit. Then continue.
     - **Stash** — Run `git stash --include-untracked -m "deploy-auto-stash"`. Restore at the end.
     - **Abort** — Stop the deploy.
3. **Fetch latest** — `git fetch origin`.
4. **Check promotion gap** — Compare `origin/test` vs `origin/main`:
   - `git rev-list --left-right --count origin/main...origin/test` → parse as `<main_ahead>\t<test_ahead>`
   - If `test_ahead` = 0: report "Nothing to deploy — test has no new commits ahead of main." Restore stash, return. Exit.
   - If `main_ahead` > 0: warn "main is ahead of test by N commits — branches have diverged. Investigate before deploying." Restore stash, return. Exit.

### Phase 1.5: Documentation Review

5. **Identify what changed** — Review `git log origin/main..origin/test --oneline` and `git diff origin/main..origin/test --stat` to understand the scope of changes being promoted.

6. **Check documentation checklist** — For each change, review the documentation checklist in `MEMORY.md` (section "Documentation Checklist") and verify that all applicable docs have been updated. At minimum, always check:
   - `CLAUDE.md`, `README.md`, `ai/context/bean-workflow.md`, `ai/context/project.md`
   - All agent files in `.claude/agents/`
   - The relevant skill and command files in `.claude/skills/` and `.claude/commands/`
   - `CHANGELOG.md`
   - `docs/` for any project documentation

7. **Search broadly** — Don't just grep for exact strings. Search for related concepts, synonyms, and soft references that may have become stale. For example, if the change modifies the team wave model, search for "wave", "BA", "Architect", "persona", "team", "decompose", etc.

8. **Update stale docs** — If any documentation is stale, checkout `test`, update the docs, commit, and push to `test` before proceeding.

9. **Skip conditions** — This phase may be skipped if the deploy contains only documentation changes (no code or workflow changes) or if the user explicitly requests a fast deploy.

### Phase 2: Quality Gate

10. **Checkout test** — `git checkout test && git pull origin test`.
11. **Run tests** — `uv run pytest` on `test`.
    - If any fail: report failures, restore stash, return to original branch. Stop.
12. **Run ruff** — `uv run ruff check foundry_app/`.

### Phase 3: Build Release Notes

13. **Identify beans** — Parse `git log origin/main..origin/test --oneline` for `BEAN-NNN:` messages. Cross-reference with `ai/beans/_index.md` for titles.
14. **Count branches to clean** — List all `bean/*` branches (local + remote). Count how many are merged into test.

### Phase 4: User Approval — ONE prompt

15. **Present summary and ask once:**
    ```
    ===================================================
    DEPLOY: test → main @ <short-sha> (tag: <tag>)
    ===================================================

    Beans: <list>
    Tests: N passed, 0 failed
    Ruff: clean / N violations

    Post-deploy: N feature branches will be deleted

    On "go": create PR test→main, merge, tag release,
    push tag, delete branches. No further prompts.
    ===================================================
    ```

16. **Single approval:** go / abort

    **CRITICAL: This is the ONLY user prompt. Everything after "go" runs without stopping.**

### Phase 5: Execute (no further prompts)

17. **Create PR to main** — `gh pr create --base main --head test --title "Release: <tag>" --body "<release notes>"`.
18. **Merge the PR** — `gh pr merge <pr-number> --merge`.
    - Do NOT delete the `test` branch — it is a permanent branch.

19. **Create tag** — Determine the tag name:
    - If `--tag <version>` was provided, use that (e.g., `v1.2.0`).
    - Otherwise, use `deploy/YYYY-MM-DD` (appending `-2`, `-3`, etc. on collision).
    - Checkout main and pull: `git checkout main && git pull origin main`.
    - Create annotated tag: `git tag -a <tag> -m "Deploy: <date> — <bean list>"`.
    - Push tag: `git push origin --tags`.

19a. **Verify claude-kit submodule is in sync** — Ensure the `.claude/kit` submodule has been pushed:
    - Run `git -C .claude/kit status --porcelain`. If dirty: warn "claude-kit submodule has uncommitted changes" and skip.
    - Run `git -C .claude/kit log @{u}..HEAD --oneline 2>/dev/null`. If there are unpushed commits: run `git -C .claude/kit push` to sync.
    - If already in sync or no upstream configured: skip.

20. **Delete local feature branches** — All `bean/*` branches merged into test: `git branch -d`. Stale/orphaned ones for Done beans: `git branch -D`.
21. **Delete remote feature branches** — Any `remotes/origin/bean/*` that are merged: `git push origin --delete`.
22. **Return to original branch** — `git checkout <original-branch>`.
23. **Restore stash** — If the user chose "Stash" in step 2: `git stash pop`. On conflict, prefer HEAD. (No action needed if the user chose "Commit".)
24. **Report success** — Tag name, commit hash, beans deployed, branches deleted.

### Phase 6: Status Check

25. **Run `/git-status`** — After the deploy report, run the `/git-status` command to show the current sync state. This confirms the deploy landed and main/test are in sync.

## Key Rules

- **One approval gate per mode.** User says "go" once. Everything after is automatic.
- **Uncommitted changes prompt.** If the working tree is dirty, the user chooses: commit, stash, or abort. Nothing is silently discarded.
- **PRs for all merges.** Both modes use `gh pr create` + `gh pr merge` for full traceability.
- **Do NOT delete source branches in Mode A.** The feature branch may still be in use.
- **Do NOT delete the `test` branch in Mode B.** It is a permanent staging branch.
- **Tag is created AND pushed** in Mode B. Not just created locally — the tag is pushed to the remote.
- **Branch cleanup happens in Mode B.** Merged feature branches are cleaned up during production deploy.
- **If a command is blocked by sandbox:** print the exact command for the user to run manually, then continue with the rest.

## Error Conditions

| Error | Resolution |
|-------|------------|
| On test or main branch (Mode A) | Switch to a feature branch first |
| Nothing to deploy (Mode B) | No new commits on test ahead of main — report and exit |
| Branches diverged (Mode B) | main is ahead of test — investigate before deploying |
| Tests fail | Report failures, restore stash, return. Fix first. |
| PR creation fails | Report error. Check `gh` auth and permissions. |
| PR merge fails | Report error. Check branch protection rules. |
| Tag already exists | Append suffix or prompt for a different tag name |
| Tag push fails | Report error. Check permissions. |
| User aborts | Restore stash, return to original branch |
| Command blocked | Print command for manual execution, continue |
