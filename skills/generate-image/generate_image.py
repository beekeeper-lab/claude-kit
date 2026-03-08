#!/usr/bin/env python3
"""Generate images using Google Gemini's Nano Banana models.

Usage:
    uv run --with google-genai --with pillow generate_image.py --prompt "..." [options]
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Model mapping — update here when model IDs change
# ---------------------------------------------------------------------------
MODEL_MAP = {
    "nanobanana2": "gemini-3.1-flash-image-preview",
    "nanobanana-pro": "gemini-3-pro-image-preview",
}

AUTO_ROUTING = {
    "draft": "nanobanana2",
    "variations": "nanobanana2",
    "edit": "nanobanana2",
    "final": "nanobanana-pro",
}

FALLBACK_ORDER = ["nanobanana-pro", "nanobanana2"]


def detect_app_name() -> str:
    """Detect the application name from project metadata.

    Checks pyproject.toml, package.json, then falls back to the directory name.
    Label values must be lowercase letters, numbers, underscores, or dashes.
    """
    import re
    cwd = Path.cwd()

    # Try pyproject.toml
    pyproject = cwd / "pyproject.toml"
    if pyproject.exists():
        for line in pyproject.read_text().splitlines():
            m = re.match(r'^name\s*=\s*["\'](.+?)["\']', line.strip())
            if m:
                return re.sub(r'[^a-z0-9_-]', '-', m.group(1).lower())

    # Try package.json
    pkg_json = cwd / "package.json"
    if pkg_json.exists():
        try:
            pkg = json.loads(pkg_json.read_text())
            if "name" in pkg:
                return re.sub(r'[^a-z0-9_-]', '-', pkg["name"].lower())
        except (json.JSONDecodeError, KeyError):
            pass

    # Fallback to directory name
    return re.sub(r'[^a-z0-9_-]', '-', cwd.name.lower())


def load_env_file():
    """Load GEMINI_API_KEY from .env file if not already in environment."""
    if os.environ.get("GEMINI_API_KEY"):
        return
    env_path = Path.cwd() / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'\"")
            if key == "GEMINI_API_KEY":
                os.environ["GEMINI_API_KEY"] = value
                return


def resolve_model(model_arg: str, quality_mode: str) -> str:
    """Resolve friendly model name to use. Returns a friendly name."""
    if model_arg != "auto":
        return model_arg
    return AUTO_ROUTING.get(quality_mode, "nanobanana2")


def assemble_prompt(args: argparse.Namespace) -> str:
    """Build the composite prompt from structured inputs."""
    parts = []
    if args.goal:
        parts.append(f"Create a {args.goal}.")
    if args.prompt:
        parts.append(args.prompt)
    if args.style:
        parts.append(f"Style: {args.style}.")
    if args.color_palette:
        parts.append(f"Use colors inspired by: {args.color_palette}.")
    if args.aspect_ratio:
        parts.append(f"Aspect ratio: {args.aspect_ratio}.")
    if args.background:
        parts.append(f"Background: {args.background}.")
    if args.text_in_image:
        parts.append(f"Text in image: {args.text_in_image}.")
    if args.negative:
        parts.append(f"Avoid: {', '.join(args.negative)}.")
    return " ".join(parts)


def generate_single_image(client, model_id: str, prompt: str, reference_images: list[Path],
                          aspect_ratio: str | None):
    """Call the Gemini API to generate one image. Returns (image_data, text, usage)."""
    from google.genai import types

    contents = []

    # Add reference images
    for ref_path in reference_images:
        mime = "image/png" if ref_path.suffix.lower() == ".png" else "image/jpeg"
        img_bytes = ref_path.read_bytes()
        contents.append(types.Part.from_bytes(data=img_bytes, mime_type=mime))

    # Add the text prompt
    contents.append(prompt)

    # Build config
    config_kwargs = {"response_modalities": ["TEXT", "IMAGE"]}
    if aspect_ratio:
        config_kwargs["image_config"] = types.ImageConfig(aspect_ratio=aspect_ratio)
    # Note: labels are tracked locally in metadata sidecars.
    # The Gemini API (AI Studio) does not support labels — only Vertex AI does.
    config = types.GenerateContentConfig(**config_kwargs)

    response = client.models.generate_content(
        model=model_id,
        contents=contents,
        config=config,
    )

    # Extract image and text from response
    image_data = None
    text_response = None
    for part in response.parts:
        if part.text is not None:
            text_response = part.text
        elif part.inline_data is not None:
            image_data = part.inline_data

    # Extract usage metadata
    usage = None
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        um = response.usage_metadata
        usage = {
            "prompt_tokens": getattr(um, "prompt_token_count", None),
            "candidates_tokens": getattr(um, "candidates_token_count", None),
            "total_tokens": getattr(um, "total_token_count", None),
        }
        if getattr(um, "candidates_tokens_details", None):
            usage["candidates_breakdown"] = [
                {"modality": str(d.modality.value), "tokens": d.token_count}
                for d in um.candidates_tokens_details
            ]

    return image_data, text_response, usage


def save_image(image_data, output_path: Path):
    """Save image data to a file."""
    if hasattr(image_data, "data"):
        raw = image_data.data
    else:
        raw = image_data
    if isinstance(raw, str):
        import base64
        raw = base64.b64decode(raw)
    output_path.write_bytes(raw)


def save_metadata(metadata: dict, output_path: Path):
    """Save metadata JSON sidecar."""
    output_path.write_text(json.dumps(metadata, indent=2) + "\n")


def fail(message: str):
    """Print error JSON and exit."""
    print(json.dumps({"success": False, "error": message}))
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Generate images with Gemini Nano Banana models")
    parser.add_argument("--prompt", type=str, default=None, help="Text description of the image")
    parser.add_argument("--model", type=str, default="auto",
                        choices=["auto", "nanobanana2", "nanobanana-pro"],
                        help="Model selection (default: auto)")
    parser.add_argument("--quality-mode", type=str, default="draft",
                        choices=["draft", "final", "edit", "variations"],
                        help="Quality mode (default: draft)")
    parser.add_argument("--goal", type=str, default=None,
                        help="What the image is for (hero image, icon, etc.)")
    parser.add_argument("--style", type=str, default=None, help="Artistic/design direction")
    parser.add_argument("--aspect-ratio", type=str, default=None,
                        help="Aspect ratio (e.g., 16:9, 1:1)")
    parser.add_argument("--background", type=str, default=None,
                        help="Background style (transparent, white, dark, etc.)")
    parser.add_argument("--text-in-image", type=str, default=None,
                        choices=["none", "minimal", "allowed", "exact"],
                        help="Text rendering rules")
    parser.add_argument("--color-palette", type=str, default=None,
                        help="Comma-separated hex values")
    parser.add_argument("--negative", action="append", default=None,
                        help="Things to avoid (repeatable)")
    parser.add_argument("--reference-image", action="append", default=None,
                        help="Path to reference image (repeatable)")
    parser.add_argument("--output-dir", type=str, default="images/misc",
                        help="Output directory (default: images/misc)")
    parser.add_argument("--asset-name", type=str, default="image",
                        help="Base filename (default: image)")
    parser.add_argument("--count", type=int, default=1,
                        help="Number of images to generate (default: 1)")

    args = parser.parse_args()

    # Validate inputs
    if not args.prompt and not args.reference_image:
        fail("--prompt is required when no --reference-image is provided.")

    if args.count < 1:
        fail("--count must be at least 1.")

    # Load API key
    load_env_file()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        fail("GEMINI_API_KEY is not set. Create a .env file with GEMINI_API_KEY=your-key "
             "or export it in your shell.")

    # Validate reference images
    reference_paths = []
    if args.reference_image:
        for ref in args.reference_image:
            p = Path(ref)
            if not p.exists():
                fail(f"Reference image not found: {ref}")
            reference_paths.append(p)

    # Resolve model
    quality_mode = args.quality_mode
    friendly_model = resolve_model(args.model, quality_mode)
    model_id = MODEL_MAP[friendly_model]

    # Assemble prompt
    assembled = assemble_prompt(args)
    if not assembled.strip():
        assembled = "Generate an image based on the provided reference images."

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Billing labels — auto-detect app name for cost tracking
    app_name = detect_app_name()
    labels = {"app": app_name, "skill": "generate-image"}

    # Initialize Gemini client
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
    except Exception as e:
        fail(f"Failed to initialize Gemini client: {e}")

    # Generate images
    results = []
    fallback_used = False
    final_model_id = model_id
    final_friendly = friendly_model

    for i in range(args.count):
        idx = f"{i + 1:02d}"
        image_file = output_dir / f"{args.asset_name}-{idx}.png"
        meta_file = output_dir / f"{args.asset_name}-{idx}.json"

        # Try primary model, fall back if needed
        image_data = None
        text_response = None
        usage = None
        generation_time_ms = None
        t_start = time.monotonic()
        try:
            image_data, text_response, usage = generate_single_image(
                client, final_model_id, assembled, reference_paths, args.aspect_ratio
            )
            generation_time_ms = round((time.monotonic() - t_start) * 1000)
        except Exception as primary_err:
            # Try fallback if we're on Pro
            if friendly_model == "nanobanana-pro":
                fallback_friendly = "nanobanana2"
                fallback_model_id = MODEL_MAP[fallback_friendly]
                t_start = time.monotonic()
                try:
                    image_data, text_response, usage = generate_single_image(
                        client, fallback_model_id, assembled, reference_paths, args.aspect_ratio
                    )
                    generation_time_ms = round((time.monotonic() - t_start) * 1000)
                    fallback_used = True
                    final_model_id = fallback_model_id
                    final_friendly = fallback_friendly
                except Exception as fallback_err:
                    fail(f"Gemini API error (primary: {primary_err}, fallback: {fallback_err})")
            else:
                fail(f"Gemini API error for model {model_id}: {primary_err}")

        if image_data is None:
            fail(f"No image was returned by the model for image {idx}. "
                 "The model may have refused the prompt or returned text only.")

        # Save image
        save_image(image_data, image_file)

        # Build metadata
        metadata = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model_requested": args.model,
            "model_resolved": final_model_id,
            "model_friendly": final_friendly,
            "quality_mode": quality_mode,
            "prompt": args.prompt,
            "assembled_prompt": assembled,
            "output_file": image_file.name,
            "output_index": i + 1,
            "labels": labels,
            "generation_time_ms": generation_time_ms,
            "fallback_used": fallback_used,
        }
        # Only include populated optional fields
        if args.goal:
            metadata["goal"] = args.goal
        if args.style:
            metadata["style"] = args.style
        if args.aspect_ratio:
            metadata["aspect_ratio"] = args.aspect_ratio
        if args.background:
            metadata["background"] = args.background
        if args.text_in_image:
            metadata["text_in_image"] = args.text_in_image
        if args.color_palette:
            metadata["color_palette"] = args.color_palette
        if args.negative:
            metadata["negative_constraints"] = args.negative
        if args.reference_image:
            metadata["reference_images"] = args.reference_image
        if text_response:
            metadata["model_text_response"] = text_response
        if usage:
            metadata["usage"] = usage

        save_metadata(metadata, meta_file)

        results.append({
            "image_path": str(image_file),
            "metadata_path": str(meta_file),
        })

    # Aggregate usage across all images
    total_usage = {"prompt_tokens": 0, "candidates_tokens": 0, "total_tokens": 0}
    for r in results:
        meta = json.loads(Path(r["metadata_path"]).read_text())
        if "usage" in meta:
            for k in total_usage:
                total_usage[k] += meta["usage"].get(k, 0) or 0

    # Output result JSON
    output = {
        "success": True,
        "model_resolved": final_model_id,
        "model_friendly": final_friendly,
        "fallback_used": fallback_used,
        "usage": total_usage,
        "images": results,
    }
    if fallback_used:
        output["warning"] = (
            f"Model '{MODEL_MAP[friendly_model]}' was unavailable. "
            f"Fell back to '{final_model_id}'."
        )

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
