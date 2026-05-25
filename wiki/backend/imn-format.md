---
title: IMN File Format
status: canonical
last_reviewed: 2026-05-23
related:
  - architecture/pipeline.md
  - architecture/overview.md
sources:
  - Backend/Python/core/agents.py
  - Backend/Python/core/imn_utils.py
  - Backend/Dreams/*.imn
---

# IMN File Format

An `.imn` ("Imagination") file is a single JSON document that holds the entire dream. It is the **primary context mechanism** between agents: each agent reads the current `.imn`, does its work, and writes back. One file per dream, named `<dream_id>.imn`.

## Where files live

- Agents write/read via `os.path.join("..", "Dreams", f"{dream_id}.imn")` — relative to the backend cwd `Backend/Python`, that resolves to **`Backend/Dreams/`**.
- ⚠️ `api_server.py`'s `DREAMS_DIR = os.path.join("Backend", "Dreams")` resolves to **`Backend/Python/Backend/Dreams/`** — a *different* directory. So `GET /api/dreams/{id}` cannot find dreams the pipeline just wrote. See [operations/status-and-roadmap.md](../operations/status-and-roadmap.md). There are stale `.imn` sets in both locations.
- Access is guarded by a file lock (`get_imn_filelock`) around `read_imn` / `write_imn` in `core/imn_utils.py`.

## Three top-level sections

### `pre_production`
Authored by the narrative agents.

| Key | Author | Meaning |
| --- | --- | --- |
| `id`, `user_id`, `created_at` | convert_prompt | identity |
| `dream_name`, `story_prompt`, `initial_goal`, `pitch` | Carthir | story concept |
| `director_vision` | CarthirReview | `{director_vision, image_prompt, visual_notes, approval_criteria}` |
| `original_director_prompt` | CarthirReview | the raw director image prompt |
| `cenedril_shot_composition` | Cenedril | **the prompt the image workflow consumes** |
| `cinematography_analysis` | Cenedril | `{word_count, *_source, perspective_validated}` |

### `in_production`
A list of scenes (Narnion appends). Each: `{scene_id, scene_context, actions: [3 choices], user_action, tap_location, object_tapped, frame_image, timestamp}`. The latest scene's `frame_image` is set to the image asset URL after generation.

### `post_production`
Written by the visual agents.

- `image_generation`: `{service: "comfy", status, workflow, prompt, prompt_id, seed, asset_url, filename, filepath, generated_at, model}`. On failure: `{service: "comfy", status: "failed", prompt, generated_at}`.
- `video_generation`: parallel block (`service: "comfy_video"`, plus `image_input`) when the video stage runs.

## Example (abridged, from a real run)

```json
{
  "pre_production": {
    "dream_name": "Glimmering Twilight",
    "story_prompt": "You have stumbled upon a mystical forest where magical mushrooms radiate...",
    "cenedril_shot_composition": "POV \"I am\" subjective camera view 1st person view...",
    "cinematography_analysis": {"word_count": 63, "perspective_validated": true}
  },
  "in_production": [
    {"scene_id": 1, "scene_context": "...clearing ahead...",
     "actions": ["Approach the crystalline structure", "Investigate the glow", "Venture deeper"],
     "frame_image": null}
  ],
  "post_production": {
    "image_generation": {"service": "comfy", "status": "failed", "prompt": "POV...", "generated_at": "2026-05-23T19:59:33Z"}
  }
}
```

## Notes

- The canonical schema reference is `Backend/Scoping/schema.imn`. The README's example schema is **older** than what the agents actually emit (it predates `cenedril_shot_composition` and the comfy `image_generation` block).
- A historical `image_generation` block used `service: "sdxl_turbo"` with in-process diffusers fields (`width`, `height`, `num_inference_steps`, `guidance_scale`, `generation_time`). New runs use the `service: "comfy"` shape above.
