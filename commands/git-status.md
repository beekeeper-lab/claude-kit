# /git-status Command

Show the sync status of all tracked branches in a clear table with actionable next steps.

## Usage

```
/git-status
```

## Process

1. **Fetch latest refs** — Run `git fetch origin` to get up-to-date remote refs without changing any local branches.
2. **Current branch** — Run `git branch --show-current`.
3. **Working tree status** — Run `git status --short`. If clean, report "Clean". If dirty, list the changed files.
4. **Get short hashes** for display:
   - `git rev-parse --short main` (local main HEAD)
   - `git rev-parse --short origin/main` (server main HEAD)
   - `git rev-parse --short test 2>/dev/null` (local test HEAD, may not exist)
   - `git rev-parse --short origin/test` (server test HEAD)
5. **Compare local ↔ server for each branch:**
   - `git rev-list --left-right --count origin/main...main` → parse as `<behind>\t<ahead>`
   - `git rev-list --left-right --count origin/test...test` → same (skip if no local `test`)
6. **Compare server test ↔ server main (deploy pipeline):**
   - `git rev-list --left-right --count origin/test...origin/main` → parse as `<test_ahead>\t<main_ahead>`
7. **Compare .claude/kit submodule ↔ its remote:**
   - Check if `.claude/kit` is a submodule: `test -f .claude/kit/.git || test -d .claude/kit/.git`
   - If not a submodule: skip this section and note "claude-kit submodule not configured"
   - Fetch latest in submodule: `git -C .claude/kit fetch origin 2>/dev/null`
   - Get local submodule HEAD: `git -C .claude/kit rev-parse --short HEAD`
   - Get remote HEAD: `git -C .claude/kit rev-parse --short origin/main`
   - Compare: `git -C .claude/kit rev-list --left-right --count origin/main...HEAD` → parse as `<behind>\t<ahead>`
   - Check if parent repo's recorded commit matches submodule HEAD: `git rev-parse --short HEAD:.claude/kit` vs `git -C .claude/kit rev-parse --short HEAD`
   - Check for uncommitted changes in submodule: `git -C .claude/kit status --porcelain`

## Output Format

Render three sections: **Working Tree**, **Branch Sync**, and **Deploy Pipeline**.

### Working Tree section

If the working tree is dirty, this is the first thing that needs attention — uncommitted changes mean the current branch is not in sync with the server.

- If clean: show `**Working tree:** ✓ Clean`
- If dirty: show `**Working tree:** ⚠ N uncommitted file(s)` followed by the file list, and the action is `Commit and push`

### Branch Sync table

Shows whether each local branch matches its remote. Use ✓ for in-sync, ⚠ for out-of-sync.

**Important:** If the working tree is dirty, the current branch row MUST show ⚠ status regardless of the commit hash comparison — uncommitted files mean it is NOT in sync with the server. The Status should read `⚠ Uncommitted changes` and the Action should read `Commit and push`.

```
### Branch Sync (local ↔ server)

| Branch | Local    | Server   | Status                  | Action Needed |
|--------|----------|----------|-------------------------|---------------|
| main   | `abc123` | `abc123` | ⚠ Uncommitted changes   | Commit and push |
| test   | `def456` | `def456` | ✓ In sync               | —             |
```

**Status and Action rules for Branch Sync (evaluated in priority order):**

| Condition | Status | Action |
|-----------|--------|--------|
| Dirty working tree on this branch | ⚠ Uncommitted changes | Commit and push |
| ahead=0, behind=0 | ✓ In sync | — |
| ahead>0, behind=0 | ⚠ N ahead | `git push origin <branch>` |
| ahead=0, behind>0 | ⚠ N behind | `git pull origin <branch>` |
| ahead>0, behind>0 | ⚠ N ahead, M behind | `git pull --rebase origin <branch>` then push |
| No local branch | — No local branch | — (server-only) |

### Deploy Pipeline table

Shows the promotion gap between `test` (staging) and `main` (production) on the server and what to do about it. Code flows: feature → test → main.

```
### Deploy Pipeline (server test → server main)

| From | To   | Gap             | Status        | Action Needed |
|------|------|-----------------|---------------|---------------|
| test | main | 2 commits ahead | ⚠ test ahead  | `/deploy`     |
```

**Status and Action rules for Deploy Pipeline:**

| Condition | Status | Action |
|-----------|--------|--------|
| test_ahead=0, main_ahead=0 | ✓ In sync | — |
| test_ahead>0, main_ahead=0 | ⚠ test ahead | Promote to production: `/deploy` |
| test_ahead=0, main_ahead>0 | ⚠ main ahead | Investigate — main should only advance via `/deploy` |
| test_ahead>0, main_ahead>0 | ⚠ Diverged | Investigate — branches have diverged |

### Claude Kit Sync table

Shows whether the `.claude/kit` submodule is in sync with its remote. Keep this in sync to share improvements across projects.

```
### Claude Kit Submodule (.claude/kit)

| Local    | Remote   | Recorded | Status    | Action Needed |
|----------|----------|----------|-----------|---------------|
| `566eff2` | `566eff2` | `566eff2` | ✓ In sync | —             |
```

- **Local** = submodule's current HEAD
- **Remote** = `origin/main` in the submodule
- **Recorded** = commit the parent repo expects (from `git rev-parse HEAD:.claude/kit`)

**Status and Action rules (evaluated in priority order):**

| Condition | Status | Action |
|-----------|--------|--------|
| Submodule has uncommitted changes | ⚠ Dirty | Commit in `.claude/kit` first |
| Local ahead of remote | ⚠ N ahead | `git -C .claude/kit push origin main` |
| Local behind remote | ⚠ N behind | `./scripts/claude-sync.sh` |
| Local != Recorded | ⚠ Pointer drift | `git add .claude/kit && git commit -m "Update claude-kit submodule"` |
| All match, clean | ✓ In sync | — |
| Not a submodule | — Not configured | Skip this section |

### Summary line

After the tables, add a one-line **Next step** that tells the user the single most important thing to do. Evaluate in this priority order (first match wins):

1. Uncommitted changes → `**Next step:** Commit and push to sync <branch> with server`
2. Local branch ahead/behind → `**Next step:** <push or pull command>`
3. Claude Kit out of sync → `**Next step:** <submodule push, pull, or pointer update command>`
4. Pipeline drift → `**Next step:** Promote test to main — run /deploy` (or investigate if main is ahead)
5. Everything clean → `All clear — nothing to do.`

## Complete Example (all in sync)

```
## Git Status

**Branch:** `main` · **Working tree:** ✓ Clean

### Branch Sync (local ↔ server)

| Branch | Local    | Server   | Status    | Action Needed |
|--------|----------|----------|-----------|---------------|
| main   | `abc123` | `abc123` | ✓ In sync | —             |
| test   | `abc123` | `abc123` | ✓ In sync | —             |

### Deploy Pipeline (server test → server main)

| From | To   | Gap | Status    | Action Needed |
|------|------|-----|-----------|---------------|
| test | main | —   | ✓ In sync | —             |

### Claude Kit Submodule (.claude/kit)

| Local    | Remote   | Recorded | Status    | Action Needed |
|----------|----------|----------|-----------|---------------|
| `566eff2` | `566eff2` | `566eff2` | ✓ In sync | —             |

All clear — nothing to do.
```

## Complete Example (claude-kit behind upstream)

```
## Git Status

**Branch:** `main` · **Working tree:** ✓ Clean

### Branch Sync (local ↔ server)

| Branch | Local    | Server   | Status    | Action Needed |
|--------|----------|----------|-----------|---------------|
| main   | `abc123` | `abc123` | ✓ In sync | —             |
| test   | `abc123` | `abc123` | ✓ In sync | —             |

### Deploy Pipeline (server test → server main)

| From | To   | Gap | Status    | Action Needed |
|------|------|-----|-----------|---------------|
| test | main | —   | ✓ In sync | —             |

### Claude Kit Submodule (.claude/kit)

| Local    | Remote   | Recorded | Status              | Action Needed              |
|----------|----------|----------|---------------------|----------------------------|
| `a1b2c3d` | `d3e4f5g` | `a1b2c3d` | ⚠ 2 behind        | `./scripts/claude-sync.sh` |

**Next step:** Update submodule — `./scripts/claude-sync.sh`
```

## Complete Example (uncommitted changes)

```
## Git Status

**Branch:** `main` · **Working tree:** ⚠ 1 uncommitted file(s)

  M .claude/commands/git-status.md

### Branch Sync (local ↔ server)

| Branch | Local    | Server   | Status                 | Action Needed   |
|--------|----------|----------|------------------------|-----------------|
| main   | `abc123` | `abc123` | ⚠ Uncommitted changes  | Commit and push |
| test   | `abc123` | `abc123` | ✓ In sync              | —               |

### Deploy Pipeline (server test → server main)

| From | To   | Gap | Status    | Action Needed |
|------|------|-----|-----------|---------------|
| test | main | —   | ✓ In sync | —             |

### Claude Kit Submodule (.claude/kit)

| Local    | Remote   | Recorded | Status    | Action Needed |
|----------|----------|----------|-----------|---------------|
| `566eff2` | `566eff2` | `566eff2` | ✓ In sync | —             |

**Next step:** Commit and push to sync main with server
```

## Complete Example (pipeline drift)

```
## Git Status

**Branch:** `main` · **Working tree:** ✓ Clean

### Branch Sync (local ↔ server)

| Branch | Local    | Server   | Status    | Action Needed |
|--------|----------|----------|-----------|---------------|
| main   | `abc123` | `abc123` | ✓ In sync | —             |
| test   | `def456` | `def456` | ✓ In sync | —             |

### Deploy Pipeline (server test → server main)

| From | To   | Gap             | Status       | Action Needed |
|------|------|-----------------|--------------|---------------|
| test | main | 2 commits ahead | ⚠ test ahead | `/deploy`     |

### Claude Kit Submodule (.claude/kit)

| Local    | Remote   | Recorded | Status    | Action Needed |
|----------|----------|----------|-----------|---------------|
| `566eff2` | `566eff2` | `566eff2` | ✓ In sync | —             |

**Next step:** Promote test to main — run `/deploy`
```
