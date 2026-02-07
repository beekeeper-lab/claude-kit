# BEAN-002: Overlay Engine Design Specification

| Field | Value |
|-------|-------|
| **Bean** | BEAN-002 |
| **Author** | Architect |
| **Status** | Final |
| **Date** | 2026-02-07 |
| **Input** | `ai/outputs/ba/bean-002-overlay-requirements.md` |

---

## 1. Component Design

### 1.1 Where Does Overlay Logic Live?

**Decision:** Introduce a new module `foundry_app/services/overlay.py` that contains all overlay-specific logic. The existing `generator.py` orchestrator gains two new parameters (`overlay` and `dry_run`) and delegates to overlay functions when `overlay=True`. Individual pipeline stages (scaffold, compile, asset_copier, seeder, safety) remain **unchanged** -- they continue to generate content as before. The overlay layer intercepts their writes.

**Rationale:** A separate `overlay.py` module keeps the overlay concern cleanly isolated. The existing stages have no awareness of overlay mode; they produce content and record file paths exactly as today. The overlay layer wraps the write operations, performing comparison and conflict detection before content hits the filesystem. This avoids scattering overlay conditionals across six different service modules.

### 1.2 Architecture Diagram

```
                           foundry-cli
                               |
                      generate_project()
                       [generator.py]
                               |
                    +----------+-----------+
                    |                      |
             overlay=False            overlay=True
             (current path)                |
                    |              load_previous_manifest()
                    |              [overlay.py]
                    |                      |
                    v                      v
          +-----------------+    +-----------------+
          | Generate to     |    | Generate to     |
          | temp directory  |    | temp directory  |
          +-----------------+    +-----------------+
                    |                      |
                    v                      v
          Write directly to       compare_trees()
          output_root             [overlay.py]
                                           |
                                           v
                                  +-----------------+
                                  | OverlayPlan     |
                                  | (create/update/ |
                                  |  skip/conflict) |
                                  +-----------------+
                                           |
                              +------------+------------+
                              |                         |
                        dry_run=True              dry_run=False
                              |                         |
                        print report             apply_plan()
                        (no writes)              [overlay.py]
                                                        |
                                                  write files
                                                  + sidecars
```

### 1.3 Two-Phase Generation Strategy

The key architectural insight is that overlay mode uses a **two-phase approach**:

1. **Phase 1: Generate to a temporary directory.** The existing pipeline runs exactly as it does today, writing all files into a temp directory. All stages (scaffold, compile, copy_assets, seed, safety) run unmodified against this temp directory.

2. **Phase 2: Compare and apply.** The `overlay.py` module compares every file in the temp directory against the overlay target directory. It classifies each file and applies the appropriate action (create, skip, conflict+sidecar, or overwrite-if-forced).

**Rationale for two-phase approach:**

- **Zero changes to existing stages.** Scaffold, compile, asset_copier, seeder, and safety continue to write files unconditionally. No `if overlay:` branches are needed in any of them.
- **Atomic preview.** The full generated tree exists before any overlay decision is made, so the comparison is complete and consistent.
- **Dry-run is trivial.** In dry-run mode, phase 2 simply reports what would happen and then deletes the temp directory. Zero filesystem side effects.
- **Addresses BA risk R-5 (partial overlay).** If phase 1 fails mid-pipeline, no files have been written to the target directory. The target remains untouched. Only a successful full generation proceeds to phase 2.

### 1.4 Per-Stage Overlay Behavior

| Stage | Overlay Awareness Needed? | Behavior in Overlay Mode |
|---|---|---|
| **Validate** | No | Runs identically. Operates on the CompositionSpec and library, not on the output directory. |
| **Scaffold** | No | Writes to the temp directory. No changes. |
| **Compile** | No | Writes compiled member prompts to the temp directory. No changes. |
| **Copy Assets** | No | Copies skills/commands/hooks to the temp directory. No changes. |
| **Seed** | No | Writes seeded tasks to the temp directory. No changes. |
| **Safety** | No | Writes settings.local.json and policy docs to the temp directory. No changes. |
| **Write Manifest** | **Yes (minor)** | The manifest records overlay metadata (see Section 5.3). The manifest is written after the overlay plan is applied, so it includes conflict/skip data. |
| **Diff Report** | **Yes (minor)** | The diff report now also includes overlay-specific sections (conflicts, orphans). Alternatively, the overlay summary replaces the diff report in overlay mode. |

### 1.5 Module Responsibilities

**`foundry_app/services/overlay.py`** (new module):

| Function | Purpose |
|---|---|
| `load_previous_manifest(target_dir)` | Load `ai/generated/manifest.json` from the target directory. Returns `None` if missing or unparseable. |
| `compare_trees(temp_dir, target_dir, previous_manifest)` | Walk the temp directory and classify every file against the target. Returns an `OverlayPlan`. |
| `apply_plan(plan, temp_dir, target_dir, force)` | Execute the overlay plan: create new files, write sidecars for conflicts (or overwrite if `force=True`), skip unchanged files. Returns an `OverlayResult`. |
| `detect_orphans(previous_manifest, current_manifest)` | Compare file lists between previous and current manifests to find orphaned files. Returns a list of orphan paths. |
| `format_overlay_report(plan, orphans)` | Format a human-readable CLI report from the overlay plan (used for both dry-run output and the post-apply summary). |
| `format_dry_run_report(plan, orphans)` | Format a detailed dry-run report (categorized: would create, would update, conflicts, unchanged, orphans). |

**`foundry_app/services/generator.py`** (modified):

- `generate_project()` gains `overlay: bool = False`, `dry_run: bool = False`, `force: bool = False` parameters.
- When `overlay=True`, the function:
  1. Sets `output_root` to a `tempfile.mkdtemp()` directory.
  2. Runs the existing pipeline stages against the temp directory.
  3. Calls `overlay.compare_trees()` to build the plan.
  4. If `dry_run=True`, calls `overlay.format_dry_run_report()` and cleans up the temp directory.
  5. If `dry_run=False`, calls `overlay.apply_plan()` and writes the manifest to the target directory.
- Returns the manifest and validation result as before, plus the `OverlayPlan` (or `None` if not in overlay mode).

**`foundry_app/cli.py`** (modified):

- New `--overlay`, `--dry-run`, `--force` flags on the `generate` subcommand.
- Mutual exclusion enforcement between `--overlay` and `--output`.
- `--dry-run` and `--force` require `--overlay`.

---

## 2. Conflict Detection Strategy

### 2.1 File Classification Algorithm

For every file `F` in the generated temp directory (relative path `rel`):

```
let target_path = target_dir / rel
let temp_content = read(temp_dir / rel)

if target_path does NOT exist:
    classify as CREATE

else:
    let existing_content = read(target_path)
    if existing_content == temp_content:  # byte-for-byte comparison
        classify as UNCHANGED
    else:
        classify as CONFLICT
```

There is no separate "UPDATE" classification in the base algorithm. A file that exists and differs is always a CONFLICT. The resolution depends on the `--force` flag:

- Without `--force`: write sidecar `<path>.foundry-new`, leave original untouched.
- With `--force`: overwrite the original, log a warning.

**Why no "UPDATE" category?** The BA requirements (US-3) define a conflict as "existing file content differs from what Foundry would generate." There is no category of files that Foundry can safely overwrite without user consent, because even files Foundry generated previously may have been hand-edited. The manifest helps _inform_ the user (see Section 2.2) but does not change the classification.

### 2.2 Manifest-Informed Provenance (Advisory, Not Authoritative)

When a previous manifest exists, the overlay engine can provide **advisory context** in the conflict report:

```
if previous_manifest is not None:
    let prev_files = collect_all_wrote_paths(previous_manifest)
    if rel in prev_files:
        conflict_reason = "File was generated by Foundry in a prior run but has been modified since."
    else:
        conflict_reason = "File exists in the overlay-managed scope but was not generated by Foundry."
else:
    conflict_reason = "File exists (no prior manifest available to determine origin)."
```

This advisory information is included in the conflict report to help the user decide whether to accept the new version. It does NOT change the classification -- a conflict is still a conflict regardless of provenance.

### 2.3 Content Comparison Method

**Byte-for-byte comparison** (v1). Read both files as bytes and compare. This is simple, predictable, and handles all file types (text and binary assets).

```python
def _files_identical(path_a: Path, path_b: Path) -> bool:
    return path_a.read_bytes() == path_b.read_bytes()
```

**Future consideration:** Store a SHA-256 hash per file in the manifest to enable faster comparison without reading both files fully. Not needed for v1 since the file count is small (typically 30-80 files per generation).

### 2.4 Conflict Report Data Structure

```python
class FileAction(BaseModel):
    """Classification of a single file in the overlay plan."""
    rel_path: str           # Relative path within the project (e.g., "ai/context/project.md")
    action: str             # "create" | "unchanged" | "conflict" | "force_overwrite"
    reason: str             # Human-readable explanation
    sidecar_path: str = ""  # Path to .foundry-new sidecar (only for conflicts without --force)

class OverlayPlan(BaseModel):
    """Complete plan for an overlay operation."""
    target_dir: str
    actions: list[FileAction] = Field(default_factory=list)
    orphans: list[str] = Field(default_factory=list)  # Files in previous manifest but not current

    @property
    def creates(self) -> list[FileAction]:
        return [a for a in self.actions if a.action == "create"]

    @property
    def unchanged(self) -> list[FileAction]:
        return [a for a in self.actions if a.action == "unchanged"]

    @property
    def conflicts(self) -> list[FileAction]:
        return [a for a in self.actions if a.action == "conflict"]

    @property
    def force_overwrites(self) -> list[FileAction]:
        return [a for a in self.actions if a.action == "force_overwrite"]
```

### 2.5 Orphan Detection

After building the overlay plan from the current generation, compare against the previous manifest:

```python
def detect_orphans(previous_manifest, current_files):
    prev_files = collect_all_wrote_paths(previous_manifest)
    return sorted(prev_files - current_files)
```

Orphaned files are reported in the summary but NOT deleted. The user receives a message like:

```
Orphaned files (generated by prior run, not in current composition):
  - .claude/agents/security-engineer.md
  - ai/generated/members/security-engineer.md
  - ai/outputs/security-engineer/README.md
Tip: Remove these manually if no longer needed.
```

---

## 3. Dry-Run Design

### 3.1 How Dry-Run Short-Circuits Writes

When `dry_run=True`:

1. Phase 1 runs normally, generating all files to a temp directory.
2. Phase 2 calls `compare_trees()` to build the `OverlayPlan`.
3. Phase 2 calls `detect_orphans()` to find orphans.
4. Phase 2 calls `format_dry_run_report()` to produce the human-readable output.
5. The temp directory is deleted via `shutil.rmtree()`.
6. **No files are written to the target directory.** No manifest update, no sidecar files, no previous-manifest backup.

The function returns a `GenerationManifest` (from the temp run), a `ValidationResult`, and the `OverlayPlan`. The manifest's `stages` reflect what the pipeline _would_ write, and the plan shows how overlay would apply it.

### 3.2 Dry-Run Output Format

```
Dry-run overlay report for: ./my-project
Composition: my-project (my-project)
Library: ./ai-team-library

Would create (12 files):
  + .claude/agents/developer.md
  + .claude/agents/architect.md
  + ai/generated/members/developer.md
  + ai/generated/members/architect.md
  + ai/tasks/seeded-tasks.md
  ...

Would skip — unchanged (5 files):
  = CLAUDE.md
  = README.md
  = ai/context/stack.md
  ...

Conflicts (2 files):
  ! ai/context/project.md
    Reason: File was generated by Foundry in a prior run but has been modified since.
    Would write sidecar: ai/context/project.md.foundry-new
  ! .claude/settings.local.json
    Reason: File was generated by Foundry in a prior run but has been modified since.
    Would write sidecar: .claude/settings.local.json.foundry-new

Orphaned files (1 file):
  ? ai/generated/members/security-engineer.md
    Tip: This file was generated by a prior run but is not in the current composition.

Summary: 12 create, 5 unchanged, 2 conflicts, 1 orphan
No files were written (dry-run mode).
```

### 3.3 Dry-Run Guarantees

- The target directory is byte-for-byte identical before and after the dry-run command.
- No `manifest.json` is written or updated.
- No `previous-manifest.json` backup is created.
- No `diff-report.md` is written.
- No `.foundry-new` sidecar files are created.
- The exit code is always 0 if validation passes (conflicts are informational, not errors).

---

## 4. CLI Interface Design

### 4.1 New Flags

Add three flags to the `generate` subcommand:

```python
gen.add_argument(
    "--overlay",
    type=Path,
    default=None,
    metavar="DIR",
    help="Overlay into an existing project directory (mutually exclusive with --output)",
)
gen.add_argument(
    "--dry-run",
    action="store_true",
    default=False,
    help="Preview overlay changes without writing (requires --overlay)",
)
gen.add_argument(
    "--force",
    action="store_true",
    default=False,
    help="Overwrite conflicting files instead of writing .foundry-new sidecars (requires --overlay)",
)
```

### 4.2 Validation Rules

Enforce in `_cmd_generate()` before calling `generate_project()`:

| Rule | Error Message |
|---|---|
| `--overlay` and `--output` both provided | `"Error: --overlay and --output are mutually exclusive."` |
| `--dry-run` without `--overlay` | `"Error: --dry-run requires --overlay."` |
| `--force` without `--overlay` | `"Error: --force requires --overlay."` |
| `--dry-run` and `--force` both provided | `"Error: --dry-run and --force are mutually exclusive."` |
| `--overlay` path does not exist | `"Error: Overlay target directory does not exist: <path>"` |
| `--overlay` path is not a directory | `"Error: Overlay target is not a directory: <path>"` |

All validation failures exit with code 1.

### 4.3 CLI Examples

```bash
# Standard generation (unchanged)
foundry-cli generate composition.yml --library ./ai-team-library

# Overlay into current directory
foundry-cli generate composition.yml --library ./ai-team-library --overlay .

# Dry-run preview before overlay
foundry-cli generate composition.yml --library ./ai-team-library --overlay . --dry-run

# Force-overwrite conflicts
foundry-cli generate composition.yml --library ./ai-team-library --overlay . --force

# Overlay into a specific project directory
foundry-cli generate composition.yml --library ./ai-team-library --overlay /path/to/my-project

# Override output directory (unchanged, NOT overlay)
foundry-cli generate composition.yml --library ./ai-team-library --output ./my-output

# INVALID: --overlay + --output
foundry-cli generate composition.yml --library ./ai-team-library --overlay . --output ./other
# => Error: --overlay and --output are mutually exclusive.

# INVALID: --dry-run without --overlay
foundry-cli generate composition.yml --library ./ai-team-library --dry-run
# => Error: --dry-run requires --overlay.
```

### 4.4 CLI Output for Overlay Mode (Non-Dry-Run)

```
Loading composition from composition.yml...
  Project: my-project (my-project)
  Stacks: python, react
  Personas: developer, architect, tech-qa

Running generation pipeline (library: ./ai-team-library, strictness: standard)...
  Generating to temporary directory...
  Comparing against overlay target: ./my-project

Overlay applied:
  Created: 12 file(s)
  Unchanged: 5 file(s)
  Conflicts: 2 file(s) — sidecars written as .foundry-new
  Orphans: 1 file(s) — see summary below

Conflict details:
  ! ai/context/project.md -> ai/context/project.md.foundry-new
  ! .claude/settings.local.json -> .claude/settings.local.json.foundry-new

Orphaned files (from prior run, not in current composition):
  ? ai/generated/members/security-engineer.md

Generation complete!
  Target: ./my-project
  Total files: 19 (12 created, 5 unchanged, 2 conflicts)
```

### 4.5 CLI Output with `--force`

```
WARNING: --force will overwrite conflicting files. Run with --dry-run first to review.

Loading composition from composition.yml...
  ...

Overlay applied (force mode):
  Created: 12 file(s)
  Unchanged: 5 file(s)
  Overwritten: 2 file(s)

Overwrite details:
  ! ai/context/project.md (overwritten)
  ! .claude/settings.local.json (overwritten)
  ...
```

### 4.6 Exit Codes

| Code | Meaning |
|---|---|
| 0 | Success. Conflicts may exist but are reported, not errors. Dry-run always exits 0 if validation passes. |
| 1 | Error: validation failure, invalid flag combination, target directory missing, unrecoverable I/O error. |

---

## 5. API Changes

### 5.1 `generate_project()` Signature

**Before:**

```python
def generate_project(
    composition: CompositionSpec,
    library_root: Path,
    output_root: Path | None = None,
    strictness: str = "standard",
) -> tuple[GenerationManifest, ValidationResult]:
```

**After:**

```python
def generate_project(
    composition: CompositionSpec,
    library_root: Path,
    output_root: Path | None = None,
    strictness: str = "standard",
    overlay: bool = False,
    dry_run: bool = False,
    force: bool = False,
) -> tuple[GenerationManifest, ValidationResult, OverlayPlan | None]:
```

**Changes:**

- Three new keyword arguments: `overlay`, `dry_run`, `force`.
- Return type gains a third element: `OverlayPlan | None`. When `overlay=False`, this is `None`. When `overlay=True`, it contains the full plan (whether dry-run or applied).
- When `overlay=True`, `output_root` is required and must point to the existing target directory. The function uses a temp directory internally for phase 1, then applies to `output_root`.

**Backward compatibility:** All new parameters have defaults. Existing callers (GUI `_cmd_generate`, tests) continue to work without changes. The third return value is additive; callers that destructure as `manifest, validation = generate_project(...)` will need a minor update to `manifest, validation, _plan = ...` or can use `result = generate_project(...)` and index.

**Alternative considered:** Return a `GenerationResult` dataclass wrapping all three values. Rejected for v1 to minimize churn; the tuple is simple and aligns with the current pattern. Can be refactored to a dataclass in a future cleanup if the return signature grows further.

### 5.2 New Types in `foundry_app/core/models.py`

```python
class FileAction(BaseModel):
    """Classification of a single file in the overlay plan."""
    rel_path: str
    action: str  # "create" | "unchanged" | "conflict" | "force_overwrite"
    reason: str = ""
    sidecar_path: str = ""


class OverlayPlan(BaseModel):
    """Complete plan for an overlay operation."""
    target_dir: str
    actions: list[FileAction] = Field(default_factory=list)
    orphans: list[str] = Field(default_factory=list)

    @property
    def creates(self) -> list[FileAction]:
        return [a for a in self.actions if a.action == "create"]

    @property
    def unchanged(self) -> list[FileAction]:
        return [a for a in self.actions if a.action == "unchanged"]

    @property
    def conflicts(self) -> list[FileAction]:
        return [a for a in self.actions if a.action == "conflict"]

    @property
    def force_overwrites(self) -> list[FileAction]:
        return [a for a in self.actions if a.action == "force_overwrite"]

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0
```

### 5.3 `GenerationManifest` Extensions

Add an optional `overlay_summary` field:

```python
class OverlaySummary(BaseModel):
    """Summary of overlay operation recorded in the manifest."""
    mode: str = "overlay"  # "overlay" | "dry_run"
    target_dir: str = ""
    files_created: int = 0
    files_unchanged: int = 0
    files_conflicted: int = 0
    files_force_overwritten: int = 0
    orphaned_files: list[str] = Field(default_factory=list)
    sidecars_written: list[str] = Field(default_factory=list)


class GenerationManifest(BaseModel):
    run_id: str = Field(...)
    library_version: str = ""
    composition_snapshot: CompositionSpec | None = None
    stages: dict[str, StageResult] = Field(default_factory=dict)
    overlay_summary: OverlaySummary | None = None  # NEW
```

The `overlay_summary` is populated after the overlay plan is applied. In dry-run mode, the manifest is not written to disk, but the in-memory manifest still has the summary for programmatic access by the caller.

### 5.4 `StageResult` -- No Changes

`StageResult` remains unchanged. It continues to record `wrote` and `warnings` for each pipeline stage. The overlay layer operates _after_ all stages have completed, so stages do not need overlay awareness. The `wrote` lists in each stage reflect what files the stage _produced_ (in the temp directory), not what was ultimately written to the target. The overlay plan provides the final ground truth for what was actually written.

### 5.5 Impact on `diff_reporter.py`

In overlay mode, the overlay plan replaces the need for a traditional diff report. However, the diff report can still be generated if `write_diff_report=True` in `GenerationOptions`. The diff reporter operates on the target directory's manifests, so it works correctly after the overlay plan has been applied and the new manifest written.

The `backup_previous_manifest()` call in `generator.py` should be moved to execute only after the overlay plan is applied (not before phase 1), since in overlay mode the manifest is in the _target_ directory, not the temp directory.

---

## 6. Key Decisions with Rationale

### D-1: Two-Phase Generation (Generate-Then-Compare)

**Decision:** Generate all files to a temp directory first, then compare against the target and apply.

**Alternatives Considered:**
- **A) Modify each stage to check before writing.** Rejected because it scatters overlay logic across 6 modules, requires every `_write` call to gain overlay awareness, and makes the overlay concern impossible to test in isolation.
- **B) Wrap the `_write` helper with a conditional writer.** Partially viable but still requires threading an overlay context through every stage. The temp-directory approach is simpler.
- **C) Post-process with rsync-like logic.** Rejected as over-engineered for the file count we deal with (30-80 files).

**Rationale:** Two-phase keeps stages pure and testable. The overlay module is independently testable. Dry-run is trivially implemented. Partial-write risk (BA R-5) is eliminated.

### D-2: Byte-for-Byte Comparison (Not Hash-Based)

**Decision:** Compare file content using byte-for-byte equality for v1.

**Alternatives Considered:**
- **A) SHA-256 hash stored in manifest.** Adds complexity (must hash at generation time, store in manifest, re-hash existing files). Provides marginal speedup for small file counts.
- **B) Modification timestamp comparison.** Unreliable -- user edits do not always update mtime, and clock skew can cause false positives.

**Rationale:** Byte comparison is simple, correct, and fast enough for the expected file count. Hash-based comparison can be added in a future iteration if performance becomes an issue.

### D-3: All Differing Files Are Conflicts (No Auto-Update)

**Decision:** Any file that exists with different content is classified as a conflict, regardless of whether Foundry generated it previously.

**Alternatives Considered:**
- **A) Auto-update files listed in the previous manifest.** Risky -- the user may have intentionally edited a Foundry-generated file. Silent overwrite violates the principle of least surprise.
- **B) Use a "managed" flag per file in the manifest to indicate whether Foundry owns it.** Adds complexity and still does not account for user edits.

**Rationale:** Conservative conflict classification protects user work. The `--force` flag provides an explicit escape hatch. The manifest provenance is used for _advisory context_ in the conflict report, not for automatic resolution.

### D-4: Sidecar Files for Conflict Resolution

**Decision:** Write the would-be content to `<path>.foundry-new` alongside the conflicting file.

**Alternatives Considered:**
- **A) Write to a separate conflicts directory** (e.g., `ai/generated/conflicts/`). Rejected because it breaks the spatial relationship between the conflicting file and the sidecar, making manual diffing harder.
- **B) Do not write sidecars; only report the conflict.** Rejected because the user would then need to re-run generation just to see the new content.

**Rationale:** Sidecar files placed adjacent to the original make `diff ai/context/project.md ai/context/project.md.foundry-new` trivial. The `.foundry-new` suffix is distinctive enough to avoid collisions.

### D-5: Overlay as a Mode of the Existing Pipeline

**Decision:** Overlay is a mode flag on `generate_project()`, not a separate tool or separate command.

**Alternatives Considered:**
- **A) Separate `overlay` subcommand in the CLI.** Rejected because overlay _is_ generation with a different write strategy. A separate subcommand would duplicate composition loading, validation, and pipeline orchestration.
- **B) Separate `foundry-overlay` CLI.** Rejected as unnecessarily fragmenting the tool surface.

**Rationale:** The overlay behavior is conceptually a modifier on the existing pipeline. All the same stages run. Only the final write strategy differs. A `--overlay` flag on the existing `generate` command is the natural interface.

### D-6: No Automatic Deletion of Orphaned Files

**Decision:** Report orphaned files but do not delete them.

**Alternatives Considered:**
- **A) Automatically delete orphans.** Rejected because this is destructive and the user may have placed custom content in the orphan's directory (e.g., persona output files beyond the scaffolded README).
- **B) Prompt the user for confirmation.** Rejected for v1 because the CLI is non-interactive in CI contexts.

**Rationale:** Listing orphans with a suggestion to remove manually is safe and informative. A `--clean-orphans` flag can be added in a future iteration.

### D-7: `--dry-run` and `--force` Are Mutually Exclusive

**Decision:** These two flags cannot be combined.

**Rationale:** `--dry-run` means "do not write anything." `--force` means "overwrite conflicts." Combining them is semantically incoherent. The CLI rejects the combination with a clear error.

---

## 7. Implementation Notes for the Developer

### 7.1 File Listing

The overlay module needs to walk the temp directory tree to build the list of generated files. Use `Path.rglob("*")` filtered to files only (skip directories). Convert all paths to relative strings using `path.relative_to(temp_dir)`.

### 7.2 Directory Creation in the Target

When applying the overlay plan, the target directory may not have all the subdirectories that the generated tree has (e.g., a new persona was added, so `ai/outputs/new-persona/` does not exist yet). The apply function must call `path.parent.mkdir(parents=True, exist_ok=True)` before writing each file, consistent with the existing `_write` helper pattern.

### 7.3 Manifest Writing in Overlay Mode

In overlay mode, the manifest is written to the _target_ directory (not the temp directory). The `backup_previous_manifest()` call should happen after phase 1 completes but before the overlay plan writes the new manifest:

```python
# In generator.py, overlay=True path:
# 1. Generate to temp_dir (all stages)
# 2. Build overlay plan
# 3. backup_previous_manifest(target_dir)  # backup the target's manifest
# 4. Apply overlay plan (writes files + new manifest to target_dir)
# 5. Clean up temp_dir
```

### 7.4 Sidecar File Tracking

Sidecar files (`.foundry-new`) should be recorded in the manifest's `overlay_summary.sidecars_written` list. This allows future runs to clean up stale sidecars (e.g., if the user resolved the conflict and the file is now unchanged).

### 7.5 Asset Copier Considerations

The asset copier uses `shutil.copytree()` and `shutil.copy2()` which copy files with metadata. In the two-phase approach, these operations happen against the temp directory, so they work correctly. The overlay comparison reads the resulting files from the temp directory and compares them byte-for-byte against the target. File metadata (timestamps, permissions) is not compared -- only content.

### 7.6 `composition.yml` Handling (EC-8)

The scaffold stage writes `ai/team/composition.yml` to the temp directory. In overlay mode, the user's composition file may be inside the target directory (the common dogfooding case). Since the composition is loaded _before_ the pipeline runs, and the scaffold stage re-serializes it from the in-memory `CompositionSpec`, this is safe. The overlay engine will compare the serialized YAML in the temp directory against the existing file in the target. If they differ (e.g., due to YAML formatting changes), it will be reported as a conflict.

### 7.7 Temporary Directory Cleanup

Use a `try/finally` block to ensure the temp directory is always cleaned up, even if an exception occurs during generation or overlay:

```python
import tempfile
temp_dir = Path(tempfile.mkdtemp(prefix="foundry-overlay-"))
try:
    # Phase 1: generate to temp_dir
    # Phase 2: compare and apply
finally:
    shutil.rmtree(temp_dir, ignore_errors=True)
```

### 7.8 Error Handling for Write Failures (EC-10)

When applying the overlay plan, wrap individual file writes in try/except. A write failure (e.g., read-only file) should:
1. Record a warning in the manifest.
2. Continue with the remaining files.
3. Include the failure in the CLI summary.

Do NOT abort the entire overlay due to a single write failure.

---

## 8. Test Guidance for Tech-QA

The following test scenarios should be covered. This section provides guidance for the Tech-QA task (Task 04).

| Category | Scenario | Key Assertion |
|---|---|---|
| Happy path | Overlay into empty project dir (first-time) | All files classified as CREATE, no conflicts |
| Happy path | Overlay with no changes (re-run same composition) | All files classified as UNCHANGED, no writes |
| Happy path | Overlay with new persona added | New persona files are CREATE, existing are UNCHANGED |
| Conflict | File hand-edited after prior generation | File is CONFLICT, sidecar written |
| Conflict | settings.local.json modified | File is CONFLICT, sidecar written |
| Force | --force overwrites conflicts | Files overwritten, warnings logged |
| Dry-run | --dry-run produces report, no writes | Target dir unchanged after command |
| Orphan | Persona removed from composition | Orphan files reported, NOT deleted |
| Error | --overlay on non-existent directory | Exit code 1, error message |
| Error | --overlay + --output | Exit code 1, error message |
| Error | --dry-run without --overlay | Exit code 1, error message |
| Error | --force without --overlay | Exit code 1, error message |
| Error | --dry-run + --force | Exit code 1, error message |
| Edge | Read-only file in target | Warning logged, other files still written |
| Edge | No previous manifest (first overlay) | All differing files are conflicts |
| Edge | Corrupted previous manifest | Falls back to no-provenance mode |

---

## 9. Scope and Limitations

### In Scope (v1)

- `--overlay`, `--dry-run`, `--force` CLI flags
- Two-phase generate-then-compare pipeline
- Byte-for-byte conflict detection
- Sidecar file writing for conflicts
- Orphan detection and reporting
- Manifest recording of overlay metadata

### Out of Scope (Future)

- **GUI support for overlay mode.** The wizard currently always creates a new project. A follow-up bean should add overlay as a generation target option in the wizard.
- **Structured merge for JSON files.** `settings.local.json` conflicts require manual resolution in v1. A future feature could merge allow/deny lists intelligently.
- **Automatic orphan cleanup (`--clean-orphans`).** Listed in orphan report as a future improvement.
- **Concurrent overlay protection (lockfile).** Documented as unsupported in v1.
- **Hash-based comparison.** Byte comparison is sufficient for v1 file counts.
- **Sidecar cleanup on subsequent runs.** Future runs could detect and remove stale `.foundry-new` files when the conflict is resolved.
