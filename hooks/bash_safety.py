#!/usr/bin/env python3
"""
Bash Safety Hook for Claude Code

Blocks dangerous bash commands:
1. Git pushes/merges to main branch
2. Force pushes
3. Dangerous rm -rf commands
4. rm commands (requires explicit approval)
5. Piping curl/wget to bash (remote code execution)
"""
import json
import re
import subprocess
import sys


def _current_branch() -> str:
    """Current git branch, or '' when not in a repo / git unavailable."""
    try:
        return subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip()
    except Exception:
        return ""


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)  # Allow on parse error

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    if tool_name != "Bash":
        sys.exit(0)

    # === HARD BLOCKS (always blocked, no exceptions) ===
    hard_blocks = [
        # Catastrophic rm commands
        (r"rm\s+(-[rf]+\s+)*/([\s;|&]|$)", "BLOCKED: Cannot delete root filesystem"),
        (r"rm\s+(-[rf]+\s+)*~([\s;|&/]|$)", "BLOCKED: Cannot delete home directory"),
        (r"rm\s+(-[rf]+\s+)*\$HOME", "BLOCKED: Cannot delete home directory"),
        (r"rm\s+-rf\s+\.([\s;|&]|$)", "BLOCKED: Cannot recursively delete current directory"),

        # Remote code execution
        (r"curl\s+.*\|\s*(ba)?sh", "BLOCKED: Cannot pipe curl to shell (security risk)"),
        (r"wget\s+.*\|\s*(ba)?sh", "BLOCKED: Cannot pipe wget to shell (security risk)"),
        (r"curl\s+.*&&\s*(ba)?sh", "BLOCKED: Cannot download and execute scripts"),
        (r"wget\s+.*&&\s*(ba)?sh", "BLOCKED: Cannot download and execute scripts"),

        # Git to main/master protection. The [\s:] alternative also catches
        # refspec pushes like `git push origin HEAD:main` / `feature:main`.
        (r"git\s+push\b[^;|&]*[\s:]main([\s;|&]|$)", "BLOCKED: Cannot push directly to main. Use a PR instead."),
        (r"git\s+push\b[^;|&]*[\s:]master([\s;|&]|$)", "BLOCKED: Cannot push directly to master. Use a PR instead."),
        (r"git\s+push\s+--force", "BLOCKED: Force push is disabled for safety"),
        (r"git\s+push\s+-f\s+", "BLOCKED: Force push is disabled for safety"),
        # Force-push via refspec (`git push origin +feature`)
        (r"git\s+push\b[^;|&]*\s\+\S", "BLOCKED: Force push (+refspec) is disabled for safety"),
    ]

    for pattern, message in hard_blocks:
        if re.search(pattern, command, re.IGNORECASE):
            print(message, file=sys.stderr)
            sys.exit(2)

    # Merging while ON a protected branch is the dangerous direction
    # (`git merge <anything>` merges INTO the current branch). Merging
    # main INTO a feature branch is a routine update and stays allowed.
    if re.search(r"git\s+merge\b", command, re.IGNORECASE):
        branch = _current_branch()
        if branch in ("main", "master", "test", "prod"):
            print(
                f"BLOCKED: Cannot merge into protected branch '{branch}'. "
                "Use a PR instead.",
                file=sys.stderr,
            )
            sys.exit(2)

    # === SOFT BLOCKS (blocked but can be overridden) ===
    # rm commands that aren't obviously safe
    safe_rm_patterns = [
        r"rm\s+(-[rf]+\s+)*(node_modules|dist|build|\.cache|__pycache__|\.pytest_cache|coverage|\.nyc_output|\.next|\.nuxt)",
        r"rm\s+(-[rf]+\s+)*\*\.(log|tmp|bak|swp)",
        r"rm\s+[^-]",  # rm without flags on a single file is usually safe
        # Non-recursive rm -f on relative paths carries the same risk as
        # plain rm; only recursive/absolute deletions need approval.
        r"rm\s+-f\s+(?![-/])",
    ]

    if re.search(r"\brm\s+", command):
        is_safe = any(re.search(p, command, re.IGNORECASE) for p in safe_rm_patterns)
        if not is_safe:
            print("BLOCKED: rm command requires explicit approval. If you need to delete files, please confirm.", file=sys.stderr)
            sys.exit(2)

    # === WARNINGS (allow but log) ===
    # git reset --hard (loses uncommitted work)
    if re.search(r"git\s+reset\s+--hard", command, re.IGNORECASE):
        # Allow but could log to audit file if desired
        pass

    sys.exit(0)  # Allow the command


if __name__ == "__main__":
    main()
