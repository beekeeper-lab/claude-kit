#!/usr/bin/env python3
"""Generate narration audio from inline ``> 🎙️`` markdown blocks via ElevenLabs.

Source of truth is the source markdown — every contiguous run of
blockquoted lines starting with the studio-microphone emoji is one
narration block. ``NARRATION-PLAN.md`` (when present) is parsed for
``Voice:`` and ``Model:`` frontmatter only — informational, not
authoritative. CLI flags override frontmatter.

Per-source-file manifests live at ``audio/<source-stem>/manifest.json``
and carry ``{index, module, audio_file, text, size_bytes}`` records.
The ``text`` field is the **stripped narration** that was sent to
ElevenLabs — bit-for-bit identical to what the API received — so
downstream build pipelines can content-hash it via
``_media_lib.text.hash_text`` for cross-page MP3 dedup.

Skip-on-disk modes (mutually composable):

    (default)               Generate every block whose MP3 is missing.
    --regenerate-changed    Also regenerate blocks whose stripped text
                            differs from the manifest's stored ``text``.
    --force                 Regenerate everything for the run.
    --dry-run               Walk + print, no API calls, no on-disk
                            changes (orphan cleanup is also skipped).
    --all                   Include auxiliary source files (every
                            ``*.md``) instead of the default
                            ``module-*.md`` glob.

Usage examples
--------------

    # Generate audio for all modules (skips existing files):
    uv run --with elevenlabs python \\
        .claude/shared/skills/generate-audio/generate_audio.py

    # Single source file:
    uv run --with elevenlabs python \\
        .claude/shared/skills/generate-audio/generate_audio.py \\
        source/module-03.md

    # Regenerate when stripped text changed:
    uv run --with elevenlabs python \\
        .claude/shared/skills/generate-audio/generate_audio.py \\
        --regenerate-changed

    # Different voice (a stock name, or a raw ElevenLabs ID):
    uv run --with elevenlabs python \\
        .claude/shared/skills/generate-audio/generate_audio.py \\
        --voice drew

Environment
-----------

``ELEVENLABS_API_KEY`` is required. The script discovers ``.env`` files
via ``_media_lib.env.load_env`` (cwd → parents → ``$HOME``); existing
process-environment values always win over file values.

Acknowledgements
----------------

The inline ``> 🎙️`` blockquote scanner, the per-source manifest
schema, the orphan-cleanup rule, and the stock-voice map are adapted
from ``Course_Material/Git_Fundamentals/scripts/generate_narration.py``
(the canonical Stonewaters reference, ~274 lines, production-tested
across an 18-course portfolio). This skill delegates markdown
stripping to ``_media_lib.text.normalize_narration_text`` (BEAN-281)
so the regex order stays in lockstep with downstream build pipelines.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# _media_lib import — works whether the script is run from the kit checkout
# or from a generated project's symlink farm.
# ---------------------------------------------------------------------------

_THIS_DIR = Path(__file__).resolve().parent
_SKILLS_ROOT = _THIS_DIR.parent
if str(_SKILLS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SKILLS_ROOT))

try:
    from _media_lib.env import load_env  # type: ignore[import-not-found]
    from _media_lib.text import normalize_narration_text  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - exercised only when symlinks broken
    def load_env(start: Path | None = None) -> dict[str, str]:  # type: ignore[misc]
        return {}

    def normalize_narration_text(text: str) -> str:  # type: ignore[misc]
        return text


# ---------------------------------------------------------------------------
# Constants — voice map (stock names ONLY), model defaults, cost rate.
# No cloned voice IDs in committed code (ADR-011 commitment 4).
# ---------------------------------------------------------------------------

DEFAULT_VOICE = "rachel"
DEFAULT_MODEL = "eleven_multilingual_v2"
DEFAULT_OUTPUT_FORMAT = "mp3_44100_128"

# Stock ElevenLabs voices that exist in any default account voice library.
# Unknown values pass through as raw IDs — the script does not validate.
STOCK_VOICE_MAP: dict[str, str] = {
    "rachel": "21m00Tcm4TlvDq8ikWAM",
    "drew": "29vD33N1CtxCmqQRPOHJ",
    "paul": "5Q0t7uMcjvnagumLfvZi",
    "sarah": "EXAVITQu4vr4xnSDxMaL",
    "emily": "LcfcDJNUP1GQjkzn1xUU",
    "charlie": "IKne3meq5aSn9XLyUdCD",
    "george": "JBFqnCBsd6RMkjVDRZzb",
    "matilda": "XrExE9yKIg1WjnnlVkGX",
}

# ElevenLabs `eleven_multilingual_v2` cost rate. **Source of truth lives
# here** — when ElevenLabs changes the rate, update this constant, not
# any docs that link to it. (Mirrors the cost-table-in-script rule in
# ADR-010 / generate-image.)
CREDITS_PER_CHAR: float = 1.0


# ---------------------------------------------------------------------------
# Inline ``> 🎙️`` blockquote scanner.
# ---------------------------------------------------------------------------

# A narration block is a contiguous run of blockquote lines starting with
# the microphone emoji. Continuation lines start with ``> `` (no emoji).
_BLOCK_RE = re.compile(
    r"(?:^|\n)(?:> 🎙️ .+(?:\n> .+)*)",
    re.MULTILINE,
)


def find_narration_blocks(markdown_text: str) -> list[dict[str, Any]]:
    """Extract narration blocks marked with 🎙️ from markdown.

    Each block is a contiguous run of blockquoted lines starting with
    the studio-microphone emoji. Continuation lines (``> ...`` without
    the emoji) are folded into the same block. Blockquotes that do
    NOT start with the emoji are ignored.

    Returns a list of ``{"index": int, "raw": str, "text": str,
    "position": int}`` dicts in document order. ``index`` is 0-based
    in this scanner; the manifest writer adds 1 to produce the 1-based
    block number used in MP3 filenames. ``text`` is the stripped
    narration via :func:`_media_lib.text.normalize_narration_text`.
    """
    blocks: list[dict[str, Any]] = []
    for i, match in enumerate(_BLOCK_RE.finditer(markdown_text)):
        raw = match.group().strip()
        text = normalize_narration_text(raw)
        blocks.append(
            {
                "index": i,
                "raw": raw,
                "text": text,
                "position": match.start(),
            }
        )
    return blocks


# ---------------------------------------------------------------------------
# NARRATION-PLAN.md frontmatter parser — informational only.
# ---------------------------------------------------------------------------

# Match ``**Key:** value`` lines in the head before the first ``##`` heading.
_FRONTMATTER_RE = re.compile(r"^\*\*([A-Za-z][A-Za-z _-]*?):\*\*\s*(.*)$")


def parse_plan_frontmatter(plan_text: str) -> dict[str, str]:
    """Parse ``Voice:`` and ``Model:`` from ``NARRATION-PLAN.md`` head.

    Only ``**Voice:**`` and ``**Model:**`` (case-insensitive on the key)
    are recognized; other keys are ignored. Parsing stops at the first
    ``## `` heading. Returns lowercase-keyed dict (``"voice"``,
    ``"model"``) — empty dict when the plan has no recognized
    frontmatter.

    Per ADR-011: this is informational. CLI flags ALWAYS win.
    """
    result: dict[str, str] = {}
    for raw_line in plan_text.splitlines():
        if raw_line.startswith("## "):
            break
        m = _FRONTMATTER_RE.match(raw_line.strip())
        if not m:
            continue
        key = m.group(1).strip().lower().replace(" ", "_").replace("-", "_")
        value = m.group(2).strip()
        if key in ("voice", "model"):
            result[key] = value
    return result


def resolve_voice(voice_name_or_id: str) -> str:
    """Resolve a voice name to an ElevenLabs voice ID.

    Stock names in :data:`STOCK_VOICE_MAP` resolve to their canonical
    voice IDs. Unknown values pass through unchanged — they may be raw
    voice IDs, names registered in the user's own ElevenLabs voice
    library, or typos. ElevenLabs validates server-side and returns a
    clear error if the ID is unknown.
    """
    return STOCK_VOICE_MAP.get(voice_name_or_id, voice_name_or_id)


# ---------------------------------------------------------------------------
# Manifest helpers.
# ---------------------------------------------------------------------------


def load_existing_manifest(module_audio_dir: Path) -> dict[int, dict[str, Any]]:
    """Load existing manifest and index by 1-based block number.

    Returns an empty dict when the manifest does not exist, fails to
    parse, or lacks the expected shape — callers treat all three as
    "no prior state" and proceed.
    """
    manifest_path = module_audio_dir / "manifest.json"
    if not manifest_path.exists():
        return {}
    try:
        entries = json.loads(manifest_path.read_text())
        return {e["index"]: e for e in entries}
    except (json.JSONDecodeError, KeyError, TypeError):
        return {}


def write_manifest(module_audio_dir: Path, entries: list[dict[str, Any]]) -> None:
    """Write the per-source manifest to ``<module_audio_dir>/manifest.json``.

    Entries are written as a JSON array with two-space indentation. The
    directory is created if missing. Callers are responsible for the
    record shape (``index, module, audio_file, text, size_bytes``); this
    helper does not validate.
    """
    module_audio_dir.mkdir(parents=True, exist_ok=True)
    (module_audio_dir / "manifest.json").write_text(
        json.dumps(entries, indent=2) + "\n"
    )


def cleanup_orphans(module_audio_dir: Path, expected_audio_files: set[str]) -> list[str]:
    """Remove MP3s whose blocks no longer exist in the current manifest.

    Returns the list of removed filenames (basenames). The directory is
    walked for ``*.mp3`` files; any name not in ``expected_audio_files``
    is removed. The function is a no-op when the directory does not
    exist. Callers MUST NOT invoke this under ``--dry-run`` — orphan
    cleanup is only correct on real generation runs.
    """
    if not module_audio_dir.is_dir():
        return []
    removed: list[str] = []
    for mp3 in sorted(module_audio_dir.glob("*.mp3")):
        if mp3.name not in expected_audio_files:
            mp3.unlink()
            removed.append(mp3.name)
    return removed


# ---------------------------------------------------------------------------
# ElevenLabs client wrapper.
# ---------------------------------------------------------------------------


def _import_elevenlabs() -> Any:
    """Lazy import of the ``elevenlabs`` SDK with a friendly error.

    The dep is not declared in ``pyproject.toml`` because the canonical
    invocation is ``uv run --with elevenlabs python <script>``; this
    function fires only when actually generating audio. Tests mock the
    SDK before ``generate_audio_for_block`` is called, so this import
    never runs under ``uv run pytest``.
    """
    try:
        from elevenlabs import ElevenLabs  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - exercised at runtime only
        raise SystemExit(
            "ERROR: elevenlabs package not installed. "
            "Run: uv run --with elevenlabs python <script>"
        ) from exc
    return ElevenLabs


def get_elevenlabs_client(api_key: str) -> Any:
    """Construct an ``ElevenLabs(api_key=...)`` client.

    Split out so tests can mock the constructor without monkey-patching
    the lazy import path.
    """
    ElevenLabs = _import_elevenlabs()
    return ElevenLabs(api_key=api_key)


def generate_audio_for_block(
    client: Any,
    text: str,
    output_path: Path,
    voice_id: str,
    model_id: str = DEFAULT_MODEL,
) -> int:
    """Generate one MP3 via ElevenLabs and write it to ``output_path``.

    The ``client`` is an already-constructed ElevenLabs SDK instance
    (see :func:`get_elevenlabs_client`); the function does not consult
    ``os.environ`` directly. It calls
    ``client.text_to_speech.convert(...)`` with the documented defaults
    (``output_format=mp3_44100_128``), concatenates the streamed bytes,
    and writes the file. Returns the file size in bytes.
    """
    audio_gen = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id=model_id,
        output_format=DEFAULT_OUTPUT_FORMAT,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    audio_bytes = b"".join(audio_gen)
    output_path.write_bytes(audio_bytes)
    return len(audio_bytes)
