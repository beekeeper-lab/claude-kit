# /deploy Command

Promotes `test` to `main` via a pull request. Runs tests, creates the PR, merges it, and cleans up — all after a single user approval.

## Usage

```
/deploy [--tag <version>]
```

- `--tag <version>` -- Optional. Tag the merge commit with a version (e.g., `v1.2.0`).

## Process

1. **Auto-stash** dirty working tree if needed (restored at end)
2. **Checkout test**, push to remote
3. **Run tests** (`uv run pytest`) and **ruff** (`uv run ruff check foundry_app/`) — stop if they fail
4. **Build release notes** from bean commits in `git log main..test`
5. **Show summary** — beans, test results, branch cleanup count
6. **One approval prompt** — user says "go", "go with tag", or "abort"
7. **Create PR** (`gh pr create --base main --head test`)
8. **Merge PR** (`gh pr merge --merge`) — preserves full commit history
9. **Tag** if requested
10. **Delete** merged feature branches (local + remote)
11. **Sync main** locally, restore stash
12. **Report** — PR URL, merge commit, beans deployed, branches deleted

## Examples

```
/deploy              # Standard deploy
/deploy --tag v2.0.0 # Deploy with version tag
```

**Approval prompt:**
```
===================================================
DEPLOY: test → main (via PR)
===================================================

Beans: BEAN-029, BEAN-030, BEAN-033
Tests: 750 passed, 0 failed
Ruff: clean

Post-merge: 3 feature branches will be deleted

On "go": create PR, merge it, delete branches,
restore working tree. No further prompts.
===================================================
```

## Error Handling

| Error | Resolution |
|-------|------------|
| Nothing to deploy | Report and exit |
| Tests fail | Report failures, stop. Fix on a bean branch first. |
| PR create fails | Check `gh auth status` and repo permissions |
| PR merge fails | Check branch protection rules or merge conflicts |
| User aborts | Restore stash, return to original branch |
| Command blocked by sandbox | Prints exact command for manual execution, continues |
