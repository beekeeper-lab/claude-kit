# /spawn-bean Command

Spawns one or more tmux windows, each running a Team Lead Claude Code agent that picks and executes a bean autonomously. Workers auto-submit their prompt and auto-close when done.

## Usage

```
/spawn-bean              # Spawn 1 window — team lead picks the best bean
/spawn-bean 16           # Spawn 1 window — team lead runs BEAN-016
/spawn-bean --count 3    # Spawn 3 windows — each team lead picks its own bean
/spawn-bean 16 17 18     # Spawn 3 windows — one per specified bean
```

## Arguments

| Argument | Description |
|----------|-------------|
| `<bean-ids...>` | Optional. One or more bean IDs (e.g., `16`, `BEAN-016`). Each gets its own window. |
| `--count N` or `-n N` | Spawn N windows. Each team lead auto-picks the highest-priority available bean. |
| *(no args)* | Spawn 1 window. Team lead auto-picks the best available bean. |

## Process

### Step 1: Determine what to spawn

- **Specific beans given** — Read `ai/beans/_index.md`. For each bean ID, verify it exists and has status `New` or `Deferred`. Resolve short IDs (e.g., `16` → `BEAN-016`). Extract the slug from the directory name.
- **`--count N`** — Read the index. Identify the top N beans by priority (High before Medium before Low) that have status `New`. You will NOT pre-assign beans — each child team lead will pick its own to avoid race conditions.
- **No args** — Same as `--count 1`.

### Step 2: Spawn each tmux window

For **each** window to spawn, create a launcher script and open a tmux window that runs it. The launcher script avoids shell quoting issues with long prompts and ensures the window auto-closes when claude exits.

```bash
# Variables — replace with actual values
BEAN_LABEL="BEAN-NNN"   # or "auto" if team lead is picking
WINDOW_NAME="bean-NNN"  # or "team-lead-1", "team-lead-2" for auto-pick
PROMPT="<prompt text from Step 3>"

# 1. Create a temp launcher script
LAUNCHER=$(mktemp /tmp/foundry-bean-XXXXXX.sh)
cat > "$LAUNCHER" << SCRIPT_EOF
#!/bin/bash
cd /home/gregg/Nextcloud/workspace/foundry
claude --dangerously-skip-permissions --agent team-lead \
  "$PROMPT"
SCRIPT_EOF
chmod +x "$LAUNCHER"

# 2. Spawn the tmux window — runs the launcher, then cleans up
#    Because we pass a command to new-window, the window auto-closes when it exits.
tmux new-window -n "${WINDOW_NAME}" "bash $LAUNCHER; rm -f $LAUNCHER"
```

**Why this works:**
- **Auto-submit**: Passing the prompt as a positional argument to `claude` makes it start interactive mode and immediately process the prompt — no `send-keys` or sleep needed.
- **Auto-close**: When `tmux new-window` runs a command (vs opening a bare shell), the window automatically closes when the command exits.
- **Clean temp files**: The launcher deletes itself after claude exits.

When spawning multiple windows, stagger by ~15 seconds so each team lead has time to claim a bean before the next one reads the index.

### Step 3: Craft the prompt

**When a specific bean is given**, the prompt should be:

```
Pick BEAN-NNN (slug) using /pick-bean NNN --start, then execute the full bean lifecycle autonomously:
1. Decompose into tasks using /seed-tasks
2. Execute each task through the appropriate team persona
3. Use /close-loop after each task to verify acceptance criteria
4. Use /handoff between persona transitions
5. Run tests (uv run pytest) and lint (uv run ruff check foundry_app/) before closing
6. Commit all changes on the feature branch
7. Use /merge-bean to merge into test
8. Use /status-report to produce final summary
Work autonomously until the bean is Done. Do not ask for user input unless you encounter an unresolvable blocker.
```

**When auto-picking** (no bean ID specified), the prompt should be:

```
You are a Team Lead. Read ai/beans/_index.md and pick the highest-priority bean with status New that is not owned by another agent. Use /pick-bean <id> --start to claim it, then execute the full bean lifecycle autonomously:
1. Decompose into tasks using /seed-tasks
2. Execute each task through the appropriate team persona
3. Use /close-loop after each task to verify acceptance criteria
4. Use /handoff between persona transitions
5. Run tests (uv run pytest) and lint (uv run ruff check foundry_app/) before closing
6. Commit all changes on the feature branch
7. Use /merge-bean to merge into test
8. Use /status-report to produce final summary
Work autonomously until the bean is Done. Do not ask for user input unless you encounter an unresolvable blocker.
```

### Step 4: Monitor workers

After all windows are spawned, report back to the user with a summary table:

```
Spawned N team lead window(s):

| Window | Bean | Status |
|--------|------|--------|
| bean-016 | BEAN-016: Core Data Models & IO Layer | Launched |
| team-lead-2 | (auto-pick) | Launched |

Monitor workers:  tmux list-windows -F '#{window_name} #{window_activity_flag}'
Switch windows:   Alt-1..9 (jump) or ` e (picker)
Check bean status: /bean-status
```

**Checking worker status from the main window:**

```bash
# List all active windows — worker windows appear as "bean-NNN"
tmux list-windows -F '#{window_name}'

# When a worker finishes (claude exits), its window auto-closes.
# Disappeared windows = completed (or failed) workers.
```

### Step 5: Cleanup

Workers clean up automatically:
- When claude exits (bean done or error), the tmux window closes automatically.
- The temp launcher script deletes itself after use.
- To force-kill a stuck worker: `tmux kill-window -t "bean-NNN"`

## Important Notes

- Each spawned Claude runs with `--dangerously-skip-permissions` and `--agent team-lead`
- Each window is named for easy identification via `Alt-N` or `` ` e `` (window picker)
- When spawning multiple auto-pick windows, stagger by ~15 seconds so each team lead has time to claim a bean before the next one reads the index — this prevents two agents from picking the same bean
- The bean locking protocol in `_index.md` provides a safety net, but staggering is still recommended
- Child agents work fully autonomously — no user input needed for normal flow
- Workers auto-close when done — no manual cleanup needed
- To check progress: `` ` e `` to list windows, or `Alt-N` to jump directly
- To check all bean status from this (coordinator) window: `/bean-status`
- Max recommended parallel windows: 3-5 (depends on system resources and API rate limits)
