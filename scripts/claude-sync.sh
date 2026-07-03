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
# SPEC-025 hardening: discovery dirs are built in a staging area and swapped
# into place (a crash or concurrent run never leaves them empty); relative
# links are computed with python3 (portable — no GNU realpath dependency);
# settings merge dedups arrays; git-hook install backs up non-kit hooks.
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
CLAUDE_DIR="${REPO_ROOT}/.claude"
KIT_SHARED="${CLAUDE_DIR}/shared"
LOCAL_DIR="${CLAUDE_DIR}/local"
STAGE_DIR="${CLAUDE_DIR}/.sync-stage"

DRY_RUN=false
CHECK_MODE=false
CONFLICTS=0
OVERRIDES=0
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

# --- Ensure submodule is initialized and at the recorded commit ---
if $DRY_RUN; then
  if [ ! -f "${KIT_SHARED}/settings.json" ]; then
    log "(dry-run) Would run: git submodule update --init --recursive"
  fi
else
  git -C "$REPO_ROOT" submodule update --init --recursive
fi

# Portable relative-path computation (macOS ships no GNU realpath).
relpath() {
  python3 -c "import os, sys; print(os.path.relpath(sys.argv[1], sys.argv[2]))" "$1" "$2"
}

# --- Helper: create a relative symlink ---
# Usage: make_link <target> <link_path> [<final_dir>]
# When building in the staging area, <final_dir> is the directory the link
# will live in AFTER the swap — relative targets must be computed against it.
make_link() {
  local target="$1"
  local link_path="$2"
  local final_dir="${3:-$(dirname "$link_path")}"
  local rel_target
  rel_target="$(relpath "$target" "$final_dir")"

  if $CHECK_MODE; then
    # In check mode, link_path is the FINAL path; verify it points correctly
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

# --- Staging: build_dir returns the directory to write links into ---
# In check mode we inspect the live dir; otherwise we build in the stage.
build_dir() {
  local asset_type="$1"
  if $CHECK_MODE; then
    echo "${CLAUDE_DIR}/${asset_type}"
    return
  fi
  local staged="${STAGE_DIR}/${asset_type}"
  if ! $DRY_RUN; then
    mkdir -p "$staged"
  fi
  echo "$staged"
}

# Swap a fully-built staged dir into place (atomic-enough: the discovery
# path is never left missing or half-built between runs).
commit_dir() {
  local asset_type="$1"
  $CHECK_MODE && return 0
  $DRY_RUN && return 0
  local staged="${STAGE_DIR}/${asset_type}"
  local final="${CLAUDE_DIR}/${asset_type}"
  local old="${STAGE_DIR}/${asset_type}.old"
  rm -rf "$old"
  if [ -d "$final" ] || [ -L "$final" ]; then
    mv "$final" "$old"
  fi
  mv "$staged" "$final"
  rm -rf "$old"
}

# --- Sync file-based assets (agents, commands, hooks) ---
# Symlinks individual files. Local overrides kit on name collision.
sync_files() {
  local asset_type="$1"       # e.g. "agents", "commands", "hooks"
  local dest_dir
  dest_dir="$(build_dir "$asset_type")"
  local final_dir="${CLAUDE_DIR}/${asset_type}"

  # Kit files first (base layer)
  local kit_dir="${KIT_SHARED}/${asset_type}"
  local local_asset_dir="${LOCAL_DIR}/${asset_type}"
  if [ -d "$kit_dir" ]; then
    for f in "$kit_dir"/*; do
      [ -f "$f" ] || continue
      local name
      name="$(basename "$f")"
      # Skip shared files that have a local override (local wins)
      if [ -f "${local_asset_dir}/${name}" ]; then
        continue
      fi
      make_link "$f" "${dest_dir}/${name}" "$final_dir"
    done
  fi

  # Local files second (override layer)
  if [ -d "$local_asset_dir" ]; then
    for f in "$local_asset_dir"/*; do
      [ -f "$f" ] || continue
      local name
      name="$(basename "$f")"
      if [ -f "${kit_dir}/${name}" ]; then
        warn "Local '${name}' overrides kit version in ${asset_type}/"
        OVERRIDES=$((OVERRIDES + 1))
      fi
      make_link "$f" "${dest_dir}/${name}" "$final_dir"
    done
  fi
}

# --- Sync internal/ subdirectory for commands (into the staged dir) ---
sync_internal_files() {
  local asset_type="$1"  # "commands"
  local dest_dir
  dest_dir="$(build_dir "$asset_type")/internal"
  local final_dir="${CLAUDE_DIR}/${asset_type}/internal"

  if ! $DRY_RUN && ! $CHECK_MODE; then
    mkdir -p "$dest_dir"
  fi

  local kit_internal="${KIT_SHARED}/${asset_type}/internal"
  local local_internal="${LOCAL_DIR}/${asset_type}/internal"
  if [ -d "$kit_internal" ]; then
    for f in "$kit_internal"/*; do
      [ -f "$f" ] || continue
      local name
      name="$(basename "$f")"
      if [ -f "${local_internal}/${name}" ]; then
        continue
      fi
      make_link "$f" "${dest_dir}/${name}" "$final_dir"
    done
  fi

  if [ -d "$local_internal" ]; then
    for f in "$local_internal"/*; do
      [ -f "$f" ] || continue
      local name
      name="$(basename "$f")"
      if [ -f "${kit_internal}/${name}" ]; then
        warn "Local internal '${name}' overrides kit version in ${asset_type}/internal/"
        OVERRIDES=$((OVERRIDES + 1))
      fi
      make_link "$f" "${dest_dir}/${name}" "$final_dir"
    done
  fi
}

# --- Sync skill directories ---
# Skills are directories containing SKILL.md, so we symlink entire dirs.
# Underscore-prefixed dirs (e.g. _media_lib) are support packages, not
# skills — never link them into the discovery path (SPEC-025).
sync_skills() {
  local dest_dir
  dest_dir="$(build_dir "skills")"
  local final_dir="${CLAUDE_DIR}/skills"

  local kit_skills="${KIT_SHARED}/skills"
  local local_skills="${LOCAL_DIR}/skills"
  if [ -d "$kit_skills" ]; then
    for d in "$kit_skills"/*/; do
      [ -d "$d" ] || continue
      local name
      name="$(basename "$d")"
      [ "$name" = "internal" ] && continue
      case "$name" in _*) continue ;; esac
      if [ -d "${local_skills}/${name}" ]; then
        continue
      fi
      make_link "$d" "${dest_dir}/${name}" "$final_dir"
    done
  fi

  if [ -d "$local_skills" ]; then
    for d in "$local_skills"/*/; do
      [ -d "$d" ] || continue
      local name
      name="$(basename "$d")"
      [ "$name" = "internal" ] && continue
      case "$name" in _*) continue ;; esac
      if [ -d "${kit_skills}/${name}" ]; then
        warn "Local skill '${name}' overrides kit version"
        OVERRIDES=$((OVERRIDES + 1))
      fi
      make_link "$d" "${dest_dir}/${name}" "$final_dir"
    done
  fi

  # Internal skills subdirectory
  local dest_internal="${dest_dir}/internal"
  local final_internal="${final_dir}/internal"
  if ! $DRY_RUN && ! $CHECK_MODE; then
    mkdir -p "$dest_internal"
  fi

  local kit_internal="${KIT_SHARED}/skills/internal"
  local local_internal="${LOCAL_DIR}/skills/internal"
  if [ -d "$kit_internal" ]; then
    for d in "$kit_internal"/*/; do
      [ -d "$d" ] || continue
      local name
      name="$(basename "$d")"
      case "$name" in _*) continue ;; esac
      if [ -d "${local_internal}/${name}" ]; then
        continue
      fi
      make_link "$d" "${dest_internal}/${name}" "$final_internal"
    done
  fi

  if [ -d "$local_internal" ]; then
    for d in "$local_internal"/*/; do
      [ -d "$d" ] || continue
      local name
      name="$(basename "$d")"
      case "$name" in _*) continue ;; esac
      if [ -d "${kit_internal}/${name}" ]; then
        warn "Local internal skill '${name}' overrides kit version"
        OVERRIDES=$((OVERRIDES + 1))
      fi
      make_link "$d" "${dest_internal}/${name}" "$final_internal"
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
            # Union with dedup (SPEC-025): re-running the merge must not
            # duplicate hook/permission entries. Dicts compare by content.
            merged = list(result[key])
            seen = {json.dumps(v, sort_keys=True) for v in merged}
            for v in value:
                key_v = json.dumps(v, sort_keys=True)
                if key_v not in seen:
                    merged.append(copy.deepcopy(v))
                    seen.add(key_v)
            result[key] = merged
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
# NOTE: Claude Code reads MCP servers from the repo-root .mcp.json, not
# .claude/mcp.json (SPEC-022). Link local MCP config to the root.
sync_mcp() {
  local local_mcp="${LOCAL_DIR}/mcp.json"
  local output="${REPO_ROOT}/.mcp.json"

  if [ -f "$local_mcp" ]; then
    if [ -e "$output" ] && [ ! -L "$output" ]; then
      warn ".mcp.json exists and is not a symlink — leaving it alone (merge local/mcp.json manually)"
      return
    fi
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
# Kit hooks first, then project-level hooks (scripts/githooks/) which win
# on name collision. Existing hooks that came from neither are backed up
# once as <name>.pre-kit instead of being silently clobbered (SPEC-025).
install_git_hooks() {
  local kit_hooks_src="${KIT_SHARED}/scripts/githooks"
  local project_hooks_src="${REPO_ROOT}/scripts/githooks"

  # Resolve the hooks directory (works in both main repo and worktrees)
  local git_dir
  git_dir="$(git -C "$REPO_ROOT" rev-parse --git-common-dir 2>/dev/null || echo "")"
  [ -n "$git_dir" ] || return 0
  local hooks_dest="${git_dir}/hooks"

  local src
  for src in "$kit_hooks_src" "$project_hooks_src"; do
    [ -d "$src" ] || continue
    for hook in "$src"/*; do
      [ -f "$hook" ] || continue
      local name
      name="$(basename "$hook")"
      local dest="${hooks_dest}/${name}"
      if $DRY_RUN; then
        log "(dry-run) Would install git hook: ${name}"
        continue
      fi
      if [ -f "$dest" ] && ! cmp -s "$hook" "$dest" \
         && [ ! -f "${dest}.pre-kit" ] \
         && ! cmp -s "${kit_hooks_src}/${name}" "$dest" 2>/dev/null \
         && ! cmp -s "${project_hooks_src}/${name}" "$dest" 2>/dev/null; then
        cp "$dest" "${dest}.pre-kit"
        warn "Existing git hook '${name}' backed up as ${name}.pre-kit"
      fi
      cp "$hook" "$dest"
      chmod +x "$dest"
      log "Installed git hook: ${name}"
    done
  done
}

# --- Main ---
log "Syncing Claude Code assets..."
log "  Shared: ${KIT_SHARED}"
log "  Local:  ${LOCAL_DIR}"
log ""

if ! $DRY_RUN && ! $CHECK_MODE; then
  rm -rf "$STAGE_DIR"
  mkdir -p "$STAGE_DIR"
fi

sync_files "agents"
sync_files "commands"
sync_internal_files "commands"
sync_files "hooks"
sync_skills
commit_dir "agents"
commit_dir "commands"
commit_dir "hooks"
commit_dir "skills"
merge_settings
sync_mcp
sync_settings_local
configure_git
install_git_hooks

if ! $DRY_RUN && ! $CHECK_MODE; then
  rm -rf "$STAGE_DIR"
fi

log ""

if $CHECK_MODE; then
  if [ "$CONFLICTS" -gt 0 ]; then
    log "CHECK FAILED: ${CONFLICTS} issue(s) found. Run scripts/claude-sync.sh to fix."
    exit 1
  else
    log "CHECK PASSED: All symlinks and settings are up to date."
    if [ "$OVERRIDES" -gt 0 ]; then
      log "(${OVERRIDES} local override(s) detected — this is expected.)"
    fi
    exit 0
  fi
fi

log "Done. ${LINKS_CREATED} symlinks created, ${OVERRIDES} override(s)."
if [ "$OVERRIDES" -gt 0 ]; then
  log "Overrides are expected when local extends kit. Review warnings above."
fi
