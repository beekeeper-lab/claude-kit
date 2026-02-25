# /deploy Command

Promotes code through the deployment pipeline using pull requests. Two modes: `/deploy test` merges the current branch into `test` (staging), and `/deploy` promotes `test` into `main` (production) with tagging and branch cleanup.

## Usage

```
/deploy test                # Merge current branch → test (staging) via PR
/deploy [--tag <version>]   # Promote test → main (production) via PR, tag release
```

| Command | What It Does |
|---------|-------------|
| `/deploy test` | Create PR from current branch → test, merge it |
| `/deploy` | Create PR from test → main, merge, tag with date-based tag, clean up branches |
| `/deploy --tag v2.0.0` | Same as above but tag with version instead of date |

## Mode A: `/deploy test` (branch → test)

1. **Check for uncommitted changes** — if dirty, prompt: **Commit**, **Stash**, or **Abort**
2. **Push current branch** to remote
3. **Run tests** (`uv run pytest`) and **ruff** (`uv run ruff check foundry_app/`) — stop if they fail
4. **Create PR** — `gh pr create --base test --head <branch>`
5. **Merge PR** — `gh pr merge --merge` (do NOT delete source branch)
6. **Sync local test** — pull latest test
7. **Return** to original branch, restore stash if applicable
8. **Run `/git-status`** — confirm merge landed

## Mode B: `/deploy` (test → main)

1. **Check for uncommitted changes** — if dirty, prompt: **Commit**, **Stash**, or **Abort**
2. **Compare `origin/test` vs `origin/main`** — exit if nothing to promote or if branches diverged
3. **Review documentation** — Check all docs in the Documentation Checklist (MEMORY.md) for stale references. Update on `test` if needed.
4. **Run tests** on `test` (`uv run pytest`) and **ruff** — stop if they fail
5. **Build release notes** from bean commits in `git log origin/main..origin/test`
6. **One approval prompt** — user says "go" or "abort"
7. **Create PR** — `gh pr create --base main --head test`
8. **Merge PR** — `gh pr merge --merge` (do NOT delete test branch)
9. **Create tag** — annotated tag with release notes, push to remote
10. **Delete** merged feature branches, local + remote
11. **Restore** stash if applicable, return to original branch
12. **Report** — tag name, commit hash, beans deployed, branches deleted
13. **Run `/git-status`** — confirm deploy landed and branches in sync

## Examples

```
/deploy test             # Push current branch to test via PR
/deploy                  # Promote test to main, tag with date
/deploy --tag v2.0.0     # Promote test to main, tag with version
```

**Mode A output (test):**
```
✓ Quality gates passed (750 tests, ruff clean)
Creating PR: feature/new-login → test
PR #42 created and merged.
Synced local test branch.
```

**Mode B approval (production):**
```
===================================================
DEPLOY: test → main @ a1b2c3d (tag: deploy/2026-02-23)
===================================================

Beans: BEAN-029, BEAN-030, BEAN-033
Tests: 750 passed, 0 failed
Ruff: clean

Post-deploy: 3 feature branches will be deleted

On "go": create PR test→main, merge, tag release,
push tag, delete branches. No further prompts.
===================================================
```

## Error Handling

| Error | Resolution |
|-------|------------|
| On test/main (Mode A) | Switch to a feature branch first |
| Nothing to deploy (Mode B) | test has no new commits ahead of main — report and exit |
| Branches diverged (Mode B) | main ahead of test — investigate first |
| Tests fail | Report failures, stop. Fix first. |
| PR creation/merge fails | Check `gh` auth and branch protection |
| Tag already exists | Append suffix or prompt for a different tag name |
| Tag push fails | Check permissions |
| Uncommitted changes | Prompted to commit, stash, or abort before proceeding |
| User aborts | Restore stash, return to original branch |
| Command blocked by sandbox | Prints exact command for manual execution, continues |
