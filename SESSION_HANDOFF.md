# Session Handoff — 2026-05-24

> Resume doc for Dreams.ai. Read `CLAUDE.md` first for durable project context; this is "what just happened / do this next."

## Headline
**Local video generation now works.** LTX-2.3 GGUF text-to-video produces coherent, on-prompt, portrait 9:16 clips on the 16 GB RTX 4080 — after a long noise-debugging saga, root-caused and fixed. Productionized into ComfyLocalMCP (`scene_video_ltx2`) and wired as Dreams' default video workflow.

## Status
- **Branch:** `main` — still uncommitted (video work + earlier ComfyLocalMCP productization not yet committed).
- **GPU stack:** ✅ image (Flux Q4 GGUF, ~55 s) and ✅ video (LTX-2.3 GGUF) both verified end-to-end.
- **ComfyUI:** shared with Valinor on `:8188`; ~15.8 GB free at rest. One job at a time; restarts are the user's call.

## What's Done (this session)
- **Diagnosed & fixed the video noise (two root causes):**
  1. The entire `ComfyUI-LTXVideo` pack (76 nodes) silently failed to import — `pyramid_blending.py` imports `pad` from `kornia.geometry.transform.pyramid`, absent in kornia 0.8.3 (latest PyPI; pack targets kornia main). **Shim applied:** `pad = F.pad` in that file (overwritten on `git pull` — upstream PR pending).
  2. **The actual noise cause:** `DualCLIPLoaderGGUF` clip2 must be `ltx-2.3-22b-dev_embeddings_connectors.safetensors` (the learned LTX connector), **NOT** `ltx-2.3_text_projection_bf16.safetensors`. clip1 = Gemma GGUF. Found by extracting the workflow embedded in `unsloth/LTX-2.3-GGUF`'s `unsloth_flowers.mp4`.
- **Productionized video (ComfyLocalMCP @ `D:\Tools\ComfyLocalMCP`):**
  - `comfy_local_mcp/workflows/scene_video_ltx2.json` — proven LTX-2.3 GGUF two-stage T2V, portrait 9:16, parameterized (prompt/negative/seed/width/height/frames/frame_rate + 7 `ltx2_*` model roles).
  - `config.py` — added 7 `ltx2_*` MODEL_ROLES.
  - `server.py` — `recommend_workflow` profile for `scene_video_ltx2`.
  - `workflows/__init__.py` — `load_workflow` now ignores undeclared logical overrides (so passing `image_input` to a T2V workflow no longer crashes; I2V workflows unaffected). Tested both paths.
- **Dreams:** `core/agents.py` `CenedrilVideoGenerator` default video workflow → `scene_video_ltx2`.
- **Timing measured:** ~5 s clip (121 frames) ≈ 263 s; ~10 s clip (241 frames) ≈ 457 s (7.6 min). ~45 s compute per second of video. `CreateVideo`→`SaveVideo` writes the mp4 natively.
- **Docs:** updated this repo's `CLAUDE.md`, ComfyLocalMCP `README.md`, Engram `Projects/dreams-ai/claude.md`; memory file `ltx23-gguf-video-works`.

## What's Pending (next, in priority order)
1. **Speed/quality adjustments** (the user's stated next focus): single-stage variant (skip upscale/refine — roughly halves time), quant tradeoffs (Q3 vs Q4_K_M unet), fewer frames, and locking **first-person POV** (currently needs explicit GoPro/own-hands/"no other person" cuing — defaults to 3rd person).
2. **Full Dreams E2E run** with `generate_video=True` to confirm `post_production.video_generation` is written (narrative → image → video). Heavy (LLM + image + video, VRAM contention) — run deliberately.
3. **Commit** the video + ComfyLocalMCP work (still uncommitted on `main`).
4. **Upstream PR** to Lightricks/ComfyUI-LTXVideo for the `pad` import (draft in chat).
5. Earlier deferred image levers: t5 fp8 swap, Flux Krea, `state["aspect_ratio"]`.

## Gotchas for Next Session
- **The connector is the whole ballgame for LTX-2.3 GGUF text:** clip2 = connectors file, not text_projection. Wrong clip2 → pure noise.
- **The kornia `pad` shim is required** for ANY LTX-2.3 advanced node to load; it's overwritten by node-pack updates.
- **LTX-2.3 fp8 checkpoint is NOT viable here** (needs 32 GB VRAM; ~0 free RAM) — GGUF is the only fit on this box.
- **Shared ComfyUI/GPU with Valinor** — free the GPU before heavy video runs; don't restart without asking.
- Plus the prior image gotchas (Flux 16-ch VAE; `update_*dependencies.bat` breaks CUDA torch) still apply — see `CLAUDE.md`.

## Reference Material
- **Working LTX-2.3 recipe + gotchas:** memory `ltx23-gguf-video-works`; `scene_video_ltx2.json` `_meta.notes`; Engram `Projects/dreams-ai/claude.md` → "Local Inference — VIDEO Verified".
- **Engram project context:** `D:\Tools\Valinor\Engram\Projects\dreams-ai\claude.md` (also at `D:\Tools\personalAI\Engram\...`, linked).
- **Aesthetic North Star:** The Archive In Between, Gloomstomper/@voidstomper (portrait 9:16 first-person dark/dreamlike shorts).
