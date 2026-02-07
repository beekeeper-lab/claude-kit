# BEAN-002: Overlay Mode Requirements

| Field | Value |
|-------|-------|
| **Bean** | BEAN-002 |
| **Author** | BA |
| **Status** | Final |
| **Date** | 2026-02-07 |

---

## 1. User Stories

### US-1: Overlay generation into an existing project

**As a** developer using Foundry to manage my project's AI scaffolding,
**I want to** run `foundry-cli generate --overlay .` against my existing project directory,
**so that** Foundry writes `.claude/` and `ai/` content directly into my project without disturbing my source code, tests, or non-Foundry configuration files.

**Acceptance Criteria:**

```gherkin
Given an existing project directory at "./my-project" containing source code, tests, and possibly prior Foundry-generated files
When I run `foundry-cli generate composition.yml --library ./ai-team-library --overlay ./my-project`
Then Foundry writes all generated files into ./my-project instead of creating a new output directory
  And only files within the overlay-managed scope (.claude/, ai/, CLAUDE.md, README.md) are created or updated
  And no files outside the overlay-managed scope are created, modified, or deleted
  And the CLI prints a summary listing every file written, skipped, or flagged as a conflict
  And the exit code is 0 if generation succeeds (even if conflicts exist)
```

```gherkin
Given an existing project with a prior Foundry generation (manifest.json exists)
When I run `foundry-cli generate --overlay .` with a modified composition (e.g., new persona added)
Then new files for the added persona are created
  And existing generated files that match the new output are left in place (no unnecessary rewrite)
  And the manifest.json is updated to reflect the new generation run
```

```gherkin
Given the --overlay flag is provided but --output is also provided
When I run `foundry-cli generate composition.yml --library ./lib --overlay ./proj --output ./other`
Then the CLI exits with an error explaining that --overlay and --output are mutually exclusive
  And no files are written
```

### US-2: Dry-run preview before overlay

**As a** developer,
**I want to** run `foundry-cli generate --overlay . --dry-run` to preview what overlay would create, update, or conflict,
**so that** I can review planned changes before committing to them.

**Acceptance Criteria:**

```gherkin
Given an existing project directory with some prior Foundry-generated content
When I run `foundry-cli generate composition.yml --library ./lib --overlay ./my-project --dry-run`
Then the CLI prints a categorized report with sections: "Would create", "Would update", "Conflicts", "Unchanged"
  And no files on disk are created, modified, or deleted
  And the exit code is 0
```

```gherkin
Given a dry-run invocation
When I inspect the filesystem after the command completes
Then no manifest.json is written or updated
  And no previous-manifest.json backup is created
  And no diff-report.md is written
  And the target directory is byte-for-byte identical to its state before the command
```

```gherkin
Given a dry-run invocation that detects conflicts
When the report is printed
Then each conflict entry includes the relative file path and the reason (e.g., "content differs from generated output")
  And the exit code is still 0 (dry-run never fails due to conflicts)
```

### US-3: Conflict detection and reporting

**As a** developer,
**I want** clear conflict reports when overlay detects that an existing file differs from what Foundry would generate,
**so that** I can decide whether to accept the Foundry version, keep my version, or manually merge.

**Acceptance Criteria:**

```gherkin
Given an existing project where ai/context/project.md has been hand-edited by the user
When I run `foundry-cli generate --overlay .` (without --dry-run)
Then the overlay engine detects that the file content differs from the newly generated content
  And the file is NOT overwritten
  And the conflict is reported in the CLI output with the file path and reason
  And the conflict is recorded in the manifest under a "conflicts" key for the relevant stage
```

```gherkin
Given a conflict is detected on a file
When overlay completes
Then Foundry writes the would-be content to a sidecar file at <original-path>.foundry-new (e.g., ai/context/project.md.foundry-new)
  And the sidecar file is recorded in the manifest
  And the user can diff the two files manually to resolve
```

```gherkin
Given the user wants to force-overwrite all conflicts
When I run `foundry-cli generate --overlay . --force`
Then all conflicting files are overwritten with the newly generated content
  And a warning is printed for each overwritten file
  And the exit code is 0
```

### US-4: Overlay respects settings.local.json customizations

**As a** developer who has manually tuned `.claude/settings.local.json` after initial generation,
**I want** overlay mode to detect my manual changes and not silently overwrite them,
**so that** my custom safety rules are preserved.

**Acceptance Criteria:**

```gherkin
Given .claude/settings.local.json exists and its content differs from what Foundry would generate
When I run `foundry-cli generate --overlay .`
Then the file is treated as a conflict (same rules as US-3)
  And the newly generated version is written to .claude/settings.local.json.foundry-new
  And the user is informed in the CLI output
```

```gherkin
Given .claude/settings.local.json exists and its content is identical to what Foundry would generate
When I run `foundry-cli generate --overlay .`
Then the file is reported as "unchanged" and not rewritten
```

---

## 2. Scope Boundary

### Overlay-Managed Files (Foundry owns these)

The overlay engine MAY create or update files within the following paths. These are the paths that the current generation pipeline (`scaffold.py`, `compiler.py`, `asset_copier.py`, `seeder.py`, `safety.py`) write to:

| Path Pattern | Written By | Notes |
|---|---|---|
| `CLAUDE.md` | scaffold.py | Project root-level context file |
| `README.md` | scaffold.py | Project root-level readme |
| `.claude/agents/*.md` | scaffold.py | Agent wrappers (one per persona with `include_agent=True`) |
| `.claude/settings.local.json` | safety.py | Safety permission rules |
| `.claude/skills/**` | asset_copier.py | Skill definitions copied from library |
| `.claude/commands/**` | asset_copier.py | Command definitions copied from library |
| `.claude/hooks/**` | asset_copier.py | Hook policy docs copied from library |
| `ai/context/project.md` | scaffold.py | Project context document |
| `ai/context/stack.md` | scaffold.py | Stack context summary |
| `ai/context/decisions.md` | scaffold.py | ADR placeholder |
| `ai/context/safety-policy.md` | safety.py | Safety policy narrative |
| `ai/context/git-policy.md` | safety.py | Git policy narrative |
| `ai/context/shell-policy.md` | safety.py | Shell policy narrative |
| `ai/team/composition.yml` | scaffold.py | Serialized composition spec |
| `ai/generated/members/*.md` | compiler.py | Compiled persona prompts |
| `ai/generated/manifest.json` | generator.py | Generation manifest |
| `ai/generated/previous-manifest.json` | diff_reporter.py | Backup of prior manifest |
| `ai/generated/diff-report.md` | diff_reporter.py | Diff report |
| `ai/tasks/*.md` | seeder.py | Seeded task files |
| `ai/outputs/<persona-id>/README.md` | scaffold.py | Per-persona output directory readme |

### User-Managed Files (Foundry NEVER touches these)

The overlay engine MUST NOT create, modify, or delete any file outside the paths listed above. Specifically:

- **Source code** -- any `src/`, `lib/`, `app/`, or language-specific source directories
- **Tests** -- `tests/`, `test/`, `spec/`, or any test directories
- **Build/config** -- `pyproject.toml`, `package.json`, `Makefile`, `Dockerfile`, `.github/`, `tsconfig.json`, etc.
- **Version control** -- `.git/`, `.gitignore`, `.gitattributes`
- **IDE/editor** -- `.vscode/`, `.idea/`, `.editorconfig`
- **Environment** -- `.env`, `.env.*`, `venv/`, `node_modules/`
- **User-created AI content** -- any files under `ai/outputs/<persona>/` that are NOT the `README.md` scaffolded by Foundry (i.e., actual persona output deliverables)
- **User-created context** -- any files under `ai/context/` that were NOT generated by Foundry (the user may add their own context documents)

### Conflict Definition

A **conflict** exists when ALL of the following are true:

1. The file path is within the overlay-managed scope (listed above).
2. The file already exists on disk.
3. The existing file content differs from what Foundry would generate in this run.

A file that exists with **identical content** to the generated output is NOT a conflict -- it is classified as "unchanged" and skipped.

A file that does NOT exist on disk is NOT a conflict -- it is classified as "new" and created.

---

## 3. Edge Cases

### EC-1: Target directory does not exist

| Aspect | Detail |
|---|---|
| **Scenario** | User runs `--overlay ./nonexistent-dir` |
| **Recommended Behavior** | Exit with error code 1 and message: "Overlay target directory does not exist: ./nonexistent-dir". Do NOT create the directory. Overlay semantics require an existing project. If the user wants a fresh project, they should use the standard `generate` command without `--overlay`. |
| **Rationale** | Creating a directory in overlay mode defeats the purpose and could mask a typo in the path. |

### EC-2: File exists with identical content

| Aspect | Detail |
|---|---|
| **Scenario** | `ai/generated/members/developer.md` exists and its content is byte-for-byte identical to what the current generation would produce. |
| **Recommended Behavior** | Skip the write. Report the file as "unchanged" in the summary. Do NOT rewrite (avoids unnecessary filesystem churn and preserves file timestamps). |
| **Rationale** | Re-writing identical files causes noise in git status, confuses file watchers, and wastes I/O. |

### EC-3: Hand-edited project context

| Aspect | Detail |
|---|---|
| **Scenario** | `ai/context/project.md` was generated by Foundry but then hand-edited by the user (e.g., the user filled in the Domain and Architecture sections). |
| **Recommended Behavior** | Treat as a conflict. Do NOT overwrite. Write the newly generated version to `ai/context/project.md.foundry-new`. Report the conflict in CLI output and manifest. |
| **Rationale** | `ai/context/project.md` is semi-owned: Foundry generates the skeleton but the user is expected to customize it. Overwriting would destroy user work. |

### EC-4: Previous manifest exists

| Aspect | Detail |
|---|---|
| **Scenario** | `ai/generated/manifest.json` exists from a prior generation run. |
| **Recommended Behavior** | Back up to `previous-manifest.json` (same as current behavior). Use the previous manifest's file list to identify files that were generated by Foundry in the prior run. This helps distinguish "user-created file in overlay scope" from "Foundry-generated file that was later modified." A file listed in the previous manifest's `stages[*].wrote` is known to be Foundry-generated. |
| **Rationale** | The manifest is the best available provenance record. Using it for conflict classification reduces false positives. |

### EC-5: settings.local.json manually modified

| Aspect | Detail |
|---|---|
| **Scenario** | The user generated a project, then manually added custom allow/deny rules to `.claude/settings.local.json`. |
| **Recommended Behavior** | Treat as a conflict (same as EC-3). Write newly generated version to `.claude/settings.local.json.foundry-new`. The user can diff and merge manually. |
| **Rationale** | `settings.local.json` is security-critical. Silent overwrite could weaken or strengthen safety rules without the user's knowledge. |

### EC-6: Overlay into a directory that was never generated by Foundry

| Aspect | Detail |
|---|---|
| **Scenario** | The user runs `--overlay .` in a project that has no prior Foundry output (no `ai/` directory, no `.claude/`, no manifest). |
| **Recommended Behavior** | Allow the overlay to proceed. All files are classified as "new" since nothing exists yet. This is the bootstrapping use case -- applying Foundry scaffolding to an existing codebase for the first time. |
| **Rationale** | This is a legitimate and important use case: adopting Foundry in a project that already has source code. |

### EC-7: Persona removed from composition between runs

| Aspect | Detail |
|---|---|
| **Scenario** | First generation included `security-engineer`. User edits composition to remove it, then re-runs overlay. |
| **Recommended Behavior** | Do NOT delete the previously generated files for the removed persona (`ai/generated/members/security-engineer.md`, `.claude/agents/security-engineer.md`, `ai/outputs/security-engineer/README.md`). Report these as "orphaned" files in the summary with a suggestion to remove them manually. |
| **Rationale** | Automatic deletion is destructive and unexpected. The user may have placed custom content in the persona's output directory. |

### EC-8: Composition file is inside the overlay target

| Aspect | Detail |
|---|---|
| **Scenario** | User runs `foundry-cli generate ai/team/composition.yml --library ./lib --overlay .` where the composition file is inside the overlay target. |
| **Recommended Behavior** | Allow this. The overlay engine reads the composition file before writing begins. The scaffold stage will overwrite `ai/team/composition.yml` with the serialized form. Since the file was loaded and is being re-serialized from the same data, this is safe. |
| **Rationale** | This is the expected dogfooding workflow: the composition lives inside the project. |

### EC-9: Concurrent overlay runs

| Aspect | Detail |
|---|---|
| **Scenario** | Two overlay processes target the same directory simultaneously. |
| **Recommended Behavior** | Out of scope for v1. Document that concurrent overlay is unsupported. The manifest backup step is not atomic, so concurrent runs could corrupt the previous-manifest.json. Consider a lockfile mechanism in a future iteration. |
| **Rationale** | Concurrency control adds significant complexity for a rare edge case. |

### EC-10: Read-only files in overlay target

| Aspect | Detail |
|---|---|
| **Scenario** | A file Foundry wants to write is read-only on the filesystem. |
| **Recommended Behavior** | Report the file as a write error in the manifest warnings. Do not abort the entire pipeline -- continue with other files. The final CLI summary should list write failures separately. |
| **Rationale** | One permission issue should not prevent the rest of the overlay from completing. |

---

## 4. Risk Register

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-1 | **Data loss from accidental overwrite.** Overlay writes to an incorrect directory and overwrites user files outside the managed scope. | Low | Critical | Strictly scope all writes to the overlay-managed file list (Section 2). Validate that output paths are within scope before writing. Require `--force` to overwrite conflicts. Implement dry-run as the recommended first step. |
| R-2 | **Silent conflict masking.** A file changes in a way that looks identical to Foundry output but was actually hand-modified (e.g., the user changed only whitespace or comments that Foundry also generates). Byte comparison misses semantic differences. | Medium | Medium | Use byte-for-byte comparison for v1 (simple, predictable). Document that Foundry compares exact content. In a future iteration, consider a content hash stored in the manifest for faster comparison. |
| R-3 | **Orphaned files accumulate over time.** As the composition evolves (personas added/removed, stacks changed), old generated files pile up because overlay never deletes. | Medium | Low | Report orphaned files (files in previous manifest but not in current generation). Provide a `--clean-orphans` flag in a future iteration. For v1, listing orphans in the summary is sufficient. |
| R-4 | **settings.local.json merge conflicts are hard to resolve.** JSON files do not merge well with text diffing. Users may struggle to reconcile Foundry-generated safety rules with their custom additions. | Medium | Medium | Write the `.foundry-new` sidecar for conflicts. In the future, consider a structured merge (union of allow/deny lists) as a separate feature. For v1, document the manual merge workflow. |
| R-5 | **Pipeline stage failure leaves partial overlay.** If compilation fails mid-way, scaffold files are already written but compiled members are not. The project is in an inconsistent state. | Low | High | The current pipeline already has this property (non-transactional writes). For overlay, document that partial writes can occur. Consider a two-phase approach in a future iteration: generate to a temp directory, then copy atomically. For v1, dry-run mitigates this by letting users preview before committing. |
| R-6 | **--force flag used carelessly.** A user runs `--overlay --force` without reviewing and overwrites customized files. | Medium | High | Print a prominent warning when `--force` is used: "WARNING: --force will overwrite N conflicting files. Run with --dry-run first to review." Require explicit confirmation if running interactively (but allow non-interactive use for CI). |
| R-7 | **Manifest file missing or corrupted.** If the previous manifest is absent or unparseable, the overlay engine cannot determine provenance of existing files. | Low | Medium | Fall back to content-comparison-only mode when no previous manifest exists. Treat all existing files in scope as potential conflicts. Log a warning that provenance information is unavailable. This is the same behavior as EC-6 (first-time overlay). |

---

## 5. CLI Interface Summary

For Architect and Developer reference, the proposed CLI changes are:

```
foundry-cli generate composition.yml --library ./lib --overlay <dir>
foundry-cli generate composition.yml --library ./lib --overlay <dir> --dry-run
foundry-cli generate composition.yml --library ./lib --overlay <dir> --force
```

| Flag | Type | Default | Description |
|---|---|---|---|
| `--overlay` | Path | (none) | Target directory for overlay mode. Mutually exclusive with `--output`. |
| `--dry-run` | bool | false | Preview changes without writing. Only valid with `--overlay`. |
| `--force` | bool | false | Overwrite conflicting files instead of writing `.foundry-new` sidecars. Only valid with `--overlay`. |

### Exit Codes

| Code | Meaning |
|---|---|
| 0 | Success (conflicts may exist but are reported, not errors) |
| 1 | Error (validation failure, target dir missing, invalid flag combination) |

---

## 6. Glossary

| Term | Definition |
|---|---|
| **Overlay** | Writing Foundry-generated files into an existing directory, merging with (not replacing) existing content. |
| **Conflict** | An overlay-managed file that exists on disk with content different from what Foundry would generate. |
| **Sidecar** | A `.foundry-new` file written alongside a conflicting file, containing the would-be generated content. |
| **Orphan** | A file that was generated by a previous Foundry run (listed in previous manifest) but is not generated by the current run (e.g., persona was removed). |
| **Overlay-managed scope** | The set of file paths that Foundry is allowed to create or update during overlay. Defined in Section 2. |
| **Provenance** | The ability to determine whether a file was generated by Foundry (via manifest records) or created/modified by the user. |

---

## Downstream Notes for Architect and Developer

1. **Architect** should design the overlay engine as a new service module (`overlay.py` or integrated into `generator.py`) that wraps the existing pipeline stages. The key new logic is: compare generated content against existing files before writing.

2. **Developer** should note that the current `_write` helper in `scaffold.py` unconditionally writes files. Overlay mode needs a conditional write path that checks for conflicts first. Consider a strategy pattern or a write-mode parameter.

3. **Tech-QA** should create tests for every edge case (EC-1 through EC-10) and every acceptance criterion in the user stories. The dry-run tests must verify zero filesystem side effects.
