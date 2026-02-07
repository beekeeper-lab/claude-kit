# BEAN-002: Overlay Implementation Notes

| Field | Value |
|-------|-------|
| **Bean** | BEAN-002 |
| **Author** | Developer |
| **Date** | 2026-02-07 |

---

## 1. What Changed and Where

### New Files

| File | Purpose |
|---|---|
| `foundry_app/services/overlay.py` | Overlay engine: compare_trees, apply_plan, detect_orphans, format_overlay_report, format_dry_run_report, load_previous_manifest, collect_all_wrote_paths |
| `tests/test_overlay.py` | 43 tests covering overlay unit tests, integration tests, and CLI flag validation |

### Modified Files

| File | Changes |
|---|---|
| `foundry_app/core/models.py` | Added `FileAction`, `OverlayPlan`, `OverlaySummary` Pydantic models; added `overlay_summary: OverlaySummary \| None` field to `GenerationManifest` |
| `foundry_app/services/generator.py` | Added `overlay`, `dry_run`, `force` params to `generate_project()`; return type is now `tuple[GenerationManifest, ValidationResult, OverlayPlan \| None]`; two-phase logic: generate to tempdir, compare, apply |
| `foundry_app/cli.py` | Added `--overlay`, `--dry-run`, `--force` flags to generate subcommand; added `_validate_overlay_flags()` helper; overlay report printing |
| `foundry_app/ui/screens/builder/wizard.py` | Updated `generate_project()` call to destructure 3-tuple |
| `foundry_app/ui/screens/builder/generate_screen.py` | Updated `generate_project()` call to destructure 3-tuple |
| `tests/test_generator.py` | Updated all `generate_project()` calls from 2-tuple to 3-tuple destructuring |
| `tests/test_cli.py` | Added `overlay=None`, `dry_run=False`, `force=False` to all `argparse.Namespace()` calls for `_cmd_generate` tests |
| `tests/test_smoke.py` | Updated `generate_project()` call to 3-tuple destructuring |

---

## 2. Architecture Summary

The overlay follows the two-phase approach from the Architect's design spec:

1. **Phase 1: Generate to temp directory.** The existing pipeline (scaffold, compile, copy_assets, seed, safety) runs unmodified against a `tempfile.mkdtemp()` directory. No changes to any stage module.

2. **Phase 2: Compare and apply.** The `overlay.py` module walks the temp directory, compares each file byte-for-byte against the target directory, and classifies as `create`, `unchanged`, `conflict`, or `force_overwrite`. The plan is then applied (or reported for dry-run).

Key design points:
- **Zero changes to existing pipeline stages.** Scaffold, compile, asset_copier, seeder, and safety remain unchanged.
- **temp dir is always cleaned up** via `try/finally` in `generate_project()`.
- **Dry-run is trivial**: skip `apply_plan()`, return the plan with a report.
- **Sidecar files** (`.foundry-new`) written alongside conflicting files for manual diffing.
- **Orphan detection** compares previous manifest's wrote paths against current generation.

---

## 3. Deviations from Design Spec

No significant deviations. Minor notes:

1. **`_run_pipeline()` helper:** Extracted the pipeline body into a private helper to keep the `try/finally` for temp dir cleanup clean. This is a structural choice not in the design spec but follows the same logic.

2. **`format_overlay_report()` and `format_dry_run_report()`:** The design spec proposed separate functions for these two cases, which is what was implemented. The `format_overlay_report()` handles both normal and force mode output.

3. **`collect_all_wrote_paths()`:** Exposed as a public function (used by both `overlay.py` and `generator.py`) rather than keeping it private to `overlay.py`.

---

## 4. Test Coverage

43 new tests in `tests/test_overlay.py`:

- **Unit tests (23):** compare_trees classification (8 tests), apply_plan execution (5 tests), detect_orphans (3 tests), load_previous_manifest (3 tests), collect_all_wrote_paths (1 test), format_overlay_report (2 tests), format_dry_run_report (1 test)
- **Integration tests (9):** overlay into empty dir, non-Foundry files untouched, unchanged files skipped, modified file conflict, force overwrite, dry-run no writes, overlay_summary in manifest, dry_run summary mode, orphan detection after persona removal
- **CLI tests (11):** 8 flag validation tests, parser test, 3 end-to-end CLI tests (overlay, dry-run, validation error)

All 291 tests pass (248 existing + 43 new).

---

## 5. Known Limitations

Per the design spec's "Out of Scope" section:

- **No GUI support for overlay mode.** The wizard still creates new projects only.
- **No structured JSON merge.** `settings.local.json` conflicts require manual resolution.
- **No automatic orphan cleanup.** Orphans are reported but not deleted.
- **No concurrent overlay protection.** No lockfile mechanism.
- **No hash-based comparison.** Byte-for-byte is sufficient for current file counts.
- **No sidecar cleanup on subsequent runs.** Stale `.foundry-new` files are not removed.

---

## 6. Backward Compatibility

- `generate_project()` return type changed from 2-tuple to 3-tuple. All existing callers updated.
- All new parameters have defaults (`overlay=False`, `dry_run=False`, `force=False`).
- CLI `_cmd_generate` now expects `overlay`, `dry_run`, `force` in the args namespace.
- The `GenerationManifest` model gained an optional `overlay_summary` field (defaults to `None`), which is fully backward-compatible with existing manifests.
