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
6. **Compare server main ↔ server test (pipeline gap):**
   - `git rev-list --left-right --count origin/test...origin/main` → parse as `<test_ahead>\t<main_ahead>`
7. **Compare .claude/kit submodule ↔ upstream:**
   - First, detect the setup: `git config --file .gitmodules submodule..claude/kit.url 2>/dev/null`
   - **If submodule-based** (the above command succeeds):
     - Check if initialized: test if `.claude/kit` is non-empty (`ls -A .claude/kit 2>/dev/null`)
     - Get pinned commit (what the parent repo expects): `git ls-tree -d HEAD .claude/kit | awk '{print $3}'` → first 7 chars
     - Fetch upstream in the submodule: `git -C .claude/kit fetch origin 2>/dev/null`
     - Get upstream HEAD: `git -C .claude/kit rev-parse origin/main 2>/dev/null` → first 7 chars
     - Compare pinned vs upstream, and count the gap: `git -C .claude/kit rev-list --left-right --count origin/main...HEAD`
   - **If subtree-based** (no submodule entry, but a `claude-kit` remote exists):
     - `git fetch claude-kit main 2>/dev/null` — fetch latest claude-kit refs
     - `git rev-parse HEAD:.claude` — tree hash of `.claude/` in foundry
     - `git rev-parse FETCH_HEAD^{tree}` — root tree hash of claude-kit main
     - If the two tree hashes match: in sync. If they differ: drift.
   - **If neither**: skip this section and note "claude-kit not configured"

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

Shows the gap between `main` and `test` on the server and what to do about it.

```
### Deploy Pipeline (server main ↔ server test)

| From | To   | Gap             | Status        | Action Needed                                                                      |
|------|------|-----------------|---------------|------------------------------------------------------------------------------------|
| main | test | 2 commits ahead | ⚠ main ahead  | Sync test: `git checkout test && git merge --ff-only main && git push origin test`  |
```

**Status and Action rules for Deploy Pipeline:**

| Condition | Status | Action |
|-----------|--------|--------|
| main_ahead=0, test_ahead=0 | ✓ In sync | — |
| main_ahead>0, test_ahead=0 | ⚠ main ahead | Sync test: `git checkout test && git merge --ff-only main && git push origin test` |
| main_ahead=0, test_ahead>0 | ⚠ test ahead | Promote: `/deploy` to tag and release main from test |
| main_ahead>0, test_ahead>0 | ⚠ Diverged | Investigate — branches have diverged |

### Claude Kit Sync table

Shows whether the `.claude/kit` submodule (or `.claude/` subtree) is in sync with its upstream. The setup is auto-detected.

#### Submodule-based repos

The section title is `### Claude Kit Submodule (.claude/kit)`. Display the first 7 characters of each commit hash.

```
### Claude Kit Submodule (.claude/kit)

| Pinned   | Upstream | Status    | Action Needed |
|----------|----------|-----------|---------------|
| `abc123` | `abc123` | ✓ In sync | —             |
```

**Status and Action rules (evaluated in priority order):**

| Condition | Status | Action |
|-----------|--------|--------|
| `.claude/kit` is empty or missing | ⚠ Not initialized | `git submodule update --init --recursive` |
| Pinned == upstream HEAD | ✓ In sync | — |
| Pinned is behind upstream (behind > 0) | ⚠ N behind upstream | `./scripts/claude-sync.sh` |
| Pinned is ahead of upstream (ahead > 0) | ⚠ N ahead of upstream | Push submodule: `cd .claude/kit && git push origin main` |
| Pinned diverged from upstream (both > 0) | ⚠ Diverged | Investigate — submodule has diverged from upstream |
| Fetch failed | ⚠ Cannot reach upstream | Check network/SSH config |

#### Subtree-based repos (fallback)

The section title is `### Claude Kit Subtree (.claude/ ↔ claude-kit)`. Display the first 7 characters of each tree hash.

```
### Claude Kit Subtree (.claude/ ↔ claude-kit)

| Local Tree | Remote Tree | Status    | Action Needed |
|------------|-------------|-----------|---------------|
| `e2487…`   | `e2487…`    | ✓ In sync | —             |
```

| Condition | Status | Action |
|-----------|--------|--------|
| Trees match | ✓ In sync | — |
| Trees differ | ⚠ Out of sync | `git subtree push --prefix=.claude claude-kit main` |
| No `claude-kit` remote | — No remote | Configure: `git remote add claude-kit git@github.com:beekeeper-lab/claude-kit.git` |

#### Neither configured

If no submodule entry and no `claude-kit` remote exist, show:

```
### Claude Kit

Not configured — see CLAUDE.md for setup instructions.
```

### Summary line

After the tables, add a one-line **Next step** that tells the user the single most important thing to do. Evaluate in this priority order (first match wins):

1. Uncommitted changes → `**Next step:** Commit and push to sync <branch> with server`
2. Local branch ahead/behind → `**Next step:** <push or pull command>`
3. Claude Kit out of sync → `**Next step:** <sync or push command>`
4. Pipeline drift → `**Next step:** <sync or deploy command>`
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

### Deploy Pipeline (server main ↔ server test)

| From | To   | Gap | Status    | Action Needed |
|------|------|-----|-----------|---------------|
| main | test | —   | ✓ In sync | —             |

### Claude Kit Submodule (.claude/kit)

| Pinned   | Upstream | Status    | Action Needed |
|----------|----------|-----------|---------------|
| `9841bc7` | `9841bc7` | ✓ In sync | —             |

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

### Deploy Pipeline (server main ↔ server test)

| From | To   | Gap | Status    | Action Needed |
|------|------|-----|-----------|---------------|
| main | test | —   | ✓ In sync | —             |

### Claude Kit Submodule (.claude/kit)

| Pinned   | Upstream | Status                  | Action Needed            |
|----------|----------|-------------------------|--------------------------|
| `9841bc7` | `566eff2` | ⚠ 3 behind upstream    | `./scripts/claude-sync.sh` |

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

### Deploy Pipeline (server main ↔ server test)

| From | To   | Gap | Status    | Action Needed |
|------|------|-----|-----------|---------------|
| main | test | —   | ✓ In sync | —             |

### Claude Kit Submodule (.claude/kit)

| Pinned   | Upstream | Status    | Action Needed |
|----------|----------|-----------|---------------|
| `9841bc7` | `9841bc7` | ✓ In sync | —             |

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

### Deploy Pipeline (server main ↔ server test)

| From | To   | Gap             | Status       | Action Needed                                                                      |
|------|------|-----------------|--------------|------------------------------------------------------------------------------------|
| main | test | 2 commits ahead | ⚠ main ahead | Sync test: `git checkout test && git merge --ff-only main && git push origin test`  |

### Claude Kit Submodule (.claude/kit)

| Pinned   | Upstream | Status    | Action Needed |
|----------|----------|-----------|---------------|
| `9841bc7` | `9841bc7` | ✓ In sync | —             |

**Next step:** Sync test to main — `git checkout test && git merge --ff-only main && git push origin test`
```
