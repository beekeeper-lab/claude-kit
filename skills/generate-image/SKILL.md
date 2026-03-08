# Skill: Generate Image

## Description

Generates image assets from text prompts using Google's Gemini image generation models (Nano Banana family). Supports model selection, quality modes, reference images, and structured design constraints.

## Trigger

Use this skill when the user asks to:
- Generate an image, icon, hero image, splash screen, or visual asset
- Create concept art, illustrations, or infographics
- Make image variations or edits based on reference images
- Create marketing graphics, card images, or background graphics
- Generate any visual asset from a text description

Also used programmatically by higher-level skills (e.g., screen generation, UI mockups).

## Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| prompt | String | Yes* | — | Text description of the image to create |
| model | String | No | `auto` | `auto`, `nanobanana2`, `nanobanana-pro` |
| quality-mode | String | No | `draft` | `draft`, `final`, `edit`, `variations` |
| goal | String | No | — | What the image is for (hero image, icon, infographic, etc.) |
| style | String | No | — | Artistic/design direction |
| aspect-ratio | String | No | — | e.g., `16:9`, `1:1`, `9:16` |
| background | String | No | — | `transparent`, `white`, `dark`, or freeform |
| text-in-image | String | No | — | `none`, `minimal`, `allowed`, `exact` |
| color-palette | String | No | — | Comma-separated hex values |
| negative | String[] | No | — | Things to avoid (repeatable) |
| reference-image | String[] | No | — | Paths to reference images (repeatable) |
| output-dir | String | No | `images/misc` | Output directory |
| asset-name | String | No | `image` | Base filename for outputs |
| count | Integer | No | `1` | Number of images (each is a separate API call) |

*`--prompt` is required unless `--reference-image` is provided.

## Models

| Friendly Name | Model ID | Use Case |
|---|---|---|
| `nanobanana2` | `gemini-3.1-flash-image-preview` | Fast, cheap. Drafts, iterations, simple graphics. |
| `nanobanana-pro` | `gemini-3-pro-image-preview` | High fidelity. Infographics, final assets, complex prompts. |

### Auto-routing (when `--model auto`)

| Quality Mode | Routes To |
|---|---|
| `draft` | `nanobanana2` |
| `variations` | `nanobanana2` |
| `edit` | `nanobanana2` |
| `final` | `nanobanana-pro` |

Explicit `--model` always overrides auto-routing.

### Fallback

If `nanobanana-pro` fails (access/quota), the script falls back to `nanobanana2` with a warning.

## Process

### Step 1: Build the command

Construct the CLI invocation from the user's request. Map natural language to CLI arguments.

```bash
uv run --with google-genai --with pillow \
  .claude/shared/skills/generate-image/generate_image.py \
  --prompt "description" \
  --model auto \
  --quality-mode draft \
  --output-dir images/project-name \
  --asset-name asset-name
```

Add optional arguments as appropriate:
- `--goal "hero image"` if the user specified what the image is for
- `--style "clean premium SaaS"` if a style was described
- `--aspect-ratio 16:9` if dimensions/ratio were mentioned
- `--background dark` if background was specified
- `--text-in-image none` if text rules were mentioned
- `--color-palette "#1F3A5F,#2D6A4F"` if colors were specified
- `--negative "no clutter" --negative "no cartoon"` for things to avoid
- `--reference-image path/to/ref.png` for reference images
- `--count 4` if multiple variations were requested

### Step 2: Execute

Run the command. The script outputs JSON to stdout.

### Step 3: Report results

Parse the JSON output and report to the user:
- Which model was used
- Number of images generated
- File paths for each image
- Any warnings (e.g., fallback from Pro to NB2)

If the script reports an error, relay the error message to the user with suggested fixes.

## Output

Images are saved as PNG files with JSON metadata sidecars:

```
images/<context>/
  <asset-name>-01.png
  <asset-name>-01.json
```

The metadata JSON records the full request parameters, assembled prompt, resolved model, and timestamp for reproducibility.

## Requirements

- `GEMINI_API_KEY` must be set in the environment or in a `.env` file at the project root
- `uv` must be available (standard for all projects using claude-kit)

## Error Conditions

| Error | Resolution |
|-------|------------|
| `GEMINI_API_KEY` not set | Create a `.env` file with `GEMINI_API_KEY=your-key` |
| Missing prompt and no reference images | Provide a `--prompt` or at least one `--reference-image` |
| Reference image not found | Check the file path |
| Model unavailable | Falls back to NB2 automatically, or errors if NB2 also fails |
| API error | Check API key, quota, and model availability |
