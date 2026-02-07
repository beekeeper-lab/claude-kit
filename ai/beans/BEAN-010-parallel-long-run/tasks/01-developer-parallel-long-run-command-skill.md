# Task 01: Create Parallel Long Run Command & Skill

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Status** | Done |
| **Depends On** | — |

## Goal

Add `--fast N` flag to `/long-run` and create the parallel execution skill. Update the Team Lead agent.

## Inputs

- `ai/beans/BEAN-010-parallel-long-run/bean.md` — acceptance criteria and architecture sketch
- `.claude/commands/long-run.md` — command to update
- `.claude/skills/long-run/SKILL.md` — skill to update
- `.claude/agents/team-lead.md` — agent to update

## Implementation

1. **`.claude/commands/long-run.md`**: Add `--fast N` flag to Usage, Inputs, Options, Process, and Examples
2. **`.claude/skills/long-run/SKILL.md`**: Add Phase 0 (tmux detection) and a parallel execution branch in the process
3. **`.claude/agents/team-lead.md`**: Update `/long-run` description to mention `--fast`

### Key Skill Additions

- **tmux detection**: Check `$TMUX` env var; if empty, instruct user to restart in tmux
- **Worker spawning**: `tmux new-window -t <session> "claude --prompt 'Process BEAN-NNN...'"` for each worker
- **Bean assignment**: Team Lead selects N independent beans (no inter-bean deps), assigns one per worker
- **Progress monitoring**: Team Lead periodically checks worker windows or reads bean status files
- **Worker recycling**: When a worker finishes, assign the next unblocked bean

## Acceptance Criteria

- [ ] `--fast N` flag documented in command and skill
- [ ] tmux detection process defined
- [ ] Worker spawning via tmux documented
- [ ] Bean assignment logic handles dependencies (no parallel dependent beans)
- [ ] Progress monitoring defined
- [ ] Team Lead agent updated
- [ ] Format matches existing patterns

## Definition of Done

Command and skill updated. All patterns documented.
