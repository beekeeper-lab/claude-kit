#!/usr/bin/env bash
#
# claude-sync.sh — Generate symlinks from shared/ and local/ into Claude Code
# discovery paths (.claude/{agents,commands,skills,hooks}/) and merge settings.
#
# Usage:
#   .claude/shared/scripts/claude-sync.sh            # run normally
#   .claude/shared/scripts/claude-sync.sh --dry-run  # preview without changes
#   .claude/shared/scripts/claude-sync.sh --check    # CI mode: verify, exit 1 if stale
#
# Run after: git clone, git pull, git submodule update
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
CLAUDE_DIR="${REPO_ROOT}/.claude"
KIT_SHARED="${CLAUDE_DIR}/shared"
LOCAL_DIR="${CLAUDE_DIR}/local"

DRY_RUN=false
CHECK_MODE=false
CONFLICTS=0
LINKS_CREATED=0

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --check)   CHECK_MODE=true; DRY_RUN=true ;;
    *) echo "Unknown argument: $arg"; exit 1 ;;
  esac
done

log()  { echo "[sync] $*"; }
warn() { echo "[sync] WARNING: $*" >&2; }

# --- Ensure submodule is initialized ---
if [ ! -f "${KIT_SHARED}/settings.json" ]; then
  log "Initializing git submodule..."
  if $DRY_RUN; then
    log "(dry-run) Would run: git submodule update --init --recursive"
  else
    git -C "$REPO_ROOT" submodule update --init --recursive
  fi
fi

# --- Helper: create a relative symlink ---
# Usage: make_link <target> <link_path>
make_link() {
  local target="$1"
  local link_path="$2"
  local link_dir
  link_dir="$(dirname "$link_path")"
  local rel_target
  rel_target="$(realpath --relative-to="$link_dir" "$target")"

  if $CHECK_MODE; then
    # In check mode, verify the symlink already exists and points correctly
    if [ -L "$link_path" ]; then
      local current
      current="$(readlink "$link_path")"
      if [ "$current" != "$rel_target" ]; then
        warn "Stale symlink: ${link_path} -> ${current} (expected ${rel_target})"
        CONFLICTS=$((CONFLICTS + 1))
      fi
    else
      warn "Missing symlink: ${link_path} -> ${rel_target}"
      CONFLICTS=$((CONFLICTS + 1))
    fi
  elif $DRY_RUN; then
    log "(dry-run) ${link_path} -> ${rel_target}"
  else
    ln -sfn "$rel_target" "$link_path"
  fi
  LINKS_CREATED=$((LINKS_CREATED + 1))
}

# --- Clean and recreate generated directories ---
clean_generated() {
  local dir="$1"
  if [ -d "$dir" ] || [ -L "$dir" ]; then
    if $DRY_RUN && ! $CHECK_MODE; then
      log "(dry-run) Would remove: $dir"
    elif ! $CHECK_MODE; then
      rm -rf "$dir"
    fi
  fi
  if ! $DRY_RUN && ! $CHECK_MODE; then
    mkdir -p "$dir"
  fi
}

# --- Sync file-based assets (agents, commands, hooks) ---
# Symlinks individual files. Local overrides kit on name collision.
sync_files() {
  local asset_type="$1"       # e.g. "agents", "commands", "hooks"
  local dest_dir="${CLAUDE_DIR}/${asset_type}"

  clean_generated "$dest_dir"

  # Kit files first (base layer)
  local kit_dir="${KIT_SHARED}/${asset_type}"
  if [ -d "$kit_dir" ]; then
    for f in "$kit_dir"/*; do
      [ -f "$f" ] || continue
      local name
      name="$(basename "$f")"
      make_link "$f" "${dest_dir}/${name}"
    done
  fi

  # Local files second (override layer)
  local local_asset_dir="${LOCAL_DIR}/${asset_type}"
  if [ -d "$local_asset_dir" ]; then
    for f in "$local_asset_dir"/*; do
      [ -f "$f" ] || continue
      local name
      name="$(basename "$f")"
      if [ -L "${dest_dir}/${name}" ]; then
        local existing_target
        existing_target="$(readlink -f "${dest_dir}/${name}")"
        if [[ "$existing_target" == *"/shared/"* ]]; then
          warn "Local '${name}' overrides kit version in ${asset_type}/"
          CONFLICTS=$((CONFLICTS + 1))
        fi
      fi
      make_link "$f" "${dest_dir}/${name}"
    done
  fi
}

# --- Sync internal/ subdirectory for commands and skills ---
sync_internal_files() {
  local asset_type="$1"  # "commands"
  local dest_dir="${CLAUDE_DIR}/${asset_type}/internal"

  if ! $DRY_RUN && ! $CHECK_MODE; then
    mkdir -p "$dest_dir"
  fi

  # Kit internal files
  local kit_internal="${KIT_SHARED}/${asset_type}/internal"
  if [ -d "$kit_internal" ]; then
    for f in "$kit_internal"/*; do
      [ -f "$f" ] || continue
      local name
      name="$(basename "$f")"
      make_link "$f" "${dest_dir}/${name}"
    done
  fi

  # Local internal files (if any exist)
  local local_internal="${LOCAL_DIR}/${asset_type}/internal"
  if [ -d "$local_internal" ]; then
    for f in "$local_internal"/*; do
      [ -f "$f" ] || continue
      local name
      name="$(basename "$f")"
      if [ -L "${dest_dir}/${name}" ]; then
        warn "Local internal '${name}' overrides kit version in ${asset_type}/internal/"
        CONFLICTS=$((CONFLICTS + 1))
      fi
      make_link "$f" "${dest_dir}/${name}"
    done
  fi
}

# --- Sync skill directories ---
# Skills are directories containing SKILL.md, so we symlink entire dirs.
sync_skills() {
  local dest_dir="${CLAUDE_DIR}/skills"

  clean_generated "$dest_dir"

  # Kit public skills
  local kit_skills="${KIT_SHARED}/skills"
  if [ -d "$kit_skills" ]; then
    for d in "$kit_skills"/*/; do
      [ -d "$d" ] || continue
      local name
      name="$(basename "$d")"
      [ "$name" = "internal" ] && continue
      make_link "$d" "${dest_dir}/${name}"
    done
  fi

  # Local public skills
  local local_skills="${LOCAL_DIR}/skills"
  if [ -d "$local_skills" ]; then
    for d in "$local_skills"/*/; do
      [ -d "$d" ] || continue
      local name
      name="$(basename "$d")"
      [ "$name" = "internal" ] && continue
      if [ -L "${dest_dir}/${name}" ]; then
        local existing_target
        existing_target="$(readlink -f "${dest_dir}/${name}")"
        if [[ "$existing_target" == *"/shared/"* ]]; then
          warn "Local skill '${name}' overrides kit version"
          CONFLICTS=$((CONFLICTS + 1))
        fi
      fi
      make_link "$d" "${dest_dir}/${name}"
    done
  fi

  # Internal skills subdirectory
  local dest_internal="${dest_dir}/internal"
  if ! $DRY_RUN && ! $CHECK_MODE; then
    mkdir -p "$dest_internal"
  fi

  # Kit internal skills
  local kit_internal="${KIT_SHARED}/skills/internal"
  if [ -d "$kit_internal" ]; then
    for d in "$kit_internal"/*/; do
      [ -d "$d" ] || continue
      local name
      name="$(basename "$d")"
      make_link "$d" "${dest_internal}/${name}"
    done
  fi

  # Local internal skills (if any exist)
  local local_internal="${LOCAL_DIR}/skills/internal"
  if [ -d "$local_internal" ]; then
    for d in "$local_internal"/*/; do
      [ -d "$d" ] || continue
      local name
      name="$(basename "$d")"
      if [ -L "${dest_internal}/${name}" ]; then
        warn "Local internal skill '${name}' overrides kit version"
        CONFLICTS=$((CONFLICTS + 1))
      fi
      make_link "$d" "${dest_internal}/${name}"
    done
  fi
}

# --- Merge settings.json (shared + local) ---
merge_settings() {
  local shared_settings="${KIT_SHARED}/settings.json"
  local local_settings="${LOCAL_DIR}/settings.json"
  local output="${CLAUDE_DIR}/settings.json"

  if [ ! -f "$shared_settings" ]; then
    warn "No shared settings.json found"
    return
  fi

  if [ ! -f "$local_settings" ]; then
    # No local settings — just symlink shared
    if $CHECK_MODE; then
      if [ -L "$output" ]; then
        local current
        current="$(readlink -f "$output")"
        if [[ "$current" != *"/shared/settings.json" ]]; then
          warn "settings.json not pointing to shared"
          CONFLICTS=$((CONFLICTS + 1))
        fi
      elif [ ! -f "$output" ]; then
        warn "Missing settings.json"
        CONFLICTS=$((CONFLICTS + 1))
      fi
    elif $DRY_RUN; then
      log "(dry-run) symlink settings.json -> shared/settings.json"
    else
      make_link "$shared_settings" "$output"
    fi
    return
  fi

  # Both exist — deep merge with embedded Python
  if $CHECK_MODE; then
    if [ ! -f "$output" ]; then
      warn "Missing merged settings.json"
      CONFLICTS=$((CONFLICTS + 1))
    fi
    return
  fi

  if $DRY_RUN; then
    log "(dry-run) Would merge shared + local settings.json"
    return
  fi

  log "Merging settings.json (shared + local)..."
  python3 -c "
import json, sys, copy

def deep_merge(base, override):
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        elif key in result and isinstance(result[key], list) and isinstance(value, list):
            result[key] = result[key] + value
        else:
            result[key] = copy.deepcopy(value)
    return result

with open('$shared_settings') as f:
    shared = json.load(f)
with open('$local_settings') as f:
    local = json.load(f)

merged = deep_merge(shared, local)

with open('$output', 'w') as f:
    json.dump(merged, f, indent=2)
    f.write('\n')
" || {
    warn "Settings merge failed, falling back to shared settings"
    make_link "$shared_settings" "$output"
  }
}

# --- Sync mcp.json from local ---
sync_mcp() {
  local local_mcp="${LOCAL_DIR}/mcp.json"
  local output="${CLAUDE_DIR}/mcp.json"

  if [ -f "$local_mcp" ]; then
    make_link "$local_mcp" "$output"
  fi
}

# --- Sync settings.local.json from local ---
sync_settings_local() {
  local local_settings_local="${LOCAL_DIR}/settings.local.json"
  local output="${CLAUDE_DIR}/settings.local.json"

  if [ -f "$local_settings_local" ]; then
    make_link "$local_settings_local" "$output"
  fi
}

# --- Configure git for submodule auto-recurse ---
configure_git() {
  if $DRY_RUN; then
    log "(dry-run) Would set git config submodule.recurse true"
    return
  fi

  if git -C "$REPO_ROOT" rev-parse --is-inside-work-tree &>/dev/null; then
    local current
    current="$(git -C "$REPO_ROOT" config --local submodule.recurse 2>/dev/null || echo "")"
    if [ "$current" != "true" ]; then
      git -C "$REPO_ROOT" config --local submodule.recurse true
      log "Set git config submodule.recurse = true"
    fi
  fi
}

# --- Install git hooks from scripts/githooks/ ---
install_git_hooks() {
  local hooks_src="${KIT_SHARED}/scripts/githooks"
  [ -d "$hooks_src" ] || return 0

  # Also check for project-level githooks
  local project_hooks_src="${REPO_ROOT}/scripts/githooks"

  # Resolve the hooks directory (works in both main repo and worktrees)
  local git_dir
  git_dir="$(git -C "$REPO_ROOT" rev-parse --git-common-dir 2>/dev/null || echo "")"
  [ -n "$git_dir" ] || return 0
  local hooks_dest="${git_dir}/hooks"

  for hook in "$hooks_src"/*; do
    [ -f "$hook" ] || continue
    local name
    name="$(basename "$hook")"
    if $DRY_RUN; then
      log "(dry-run) Would install git hook: ${name}"
    else
      cp "$hook" "${hooks_dest}/${name}"
      chmod +x "${hooks_dest}/${name}"
      log "Installed git hook: ${name}"
    fi
  done
}

# --- Main ---
log "Syncing Claude Code assets..."
log "  Shared: ${KIT_SHARED}"
log "  Local:  ${LOCAL_DIR}"
log ""

sync_files "agents"
sync_files "commands"
sync_internal_files "commands"
sync_files "hooks"
sync_skills
merge_settings
sync_mcp
sync_settings_local
configure_git
install_git_hooks

log ""

if $CHECK_MODE; then
  if [ "$CONFLICTS" -gt 0 ]; then
    log "CHECK FAILED: ${CONFLICTS} issue(s) found. Run scripts/claude-sync.sh to fix."
    exit 1
  else
    log "CHECK PASSED: All symlinks and settings are up to date."
    exit 0
  fi
fi

log "Done. ${LINKS_CREATED} symlinks created, ${CONFLICTS} override(s)."
if [ "$CONFLICTS" -gt 0 ]; then
  warn "Override conflicts are expected when local extends kit. Review warnings above."
fi
