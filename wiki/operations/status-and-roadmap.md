---
title: Status & Roadmap
status: canonical
last_reviewed: 2026-05-23
related:
  - architecture/pipeline.md
  - architecture/visual-generation.md
  - operations/testing.md
sources:
  - end-to-end run 2026-05-23
  - CLAUDE.md
  - SESSION_HANDOFF.md
---

# Status & Roadmap

The living "where are we" doc: **what works**, **what's broken**, **what can be removed**, and **what's next**. Grounded in the end-to-end run on 2026-05-23.

## What we have (works today)

- **Full narrative pipeline.** `POST /api/dream` → Carthir → Narnion → CarthirReview → Cenedril produces a complete, coherent `.imn` in **~11.6 s** (4 Llama-3.1 8B calls on the 4080). Verified 2026-05-23: dream name, pitch, one scene with 3 actions, director vision, first-person shot composition — all well-formed.
- **LangGraph orchestration.** Sequential supervisor routing through `pipeline_step` works reliably ([pipeline.md](../architecture/pipeline.md)).
- **LLM serving.** llama-cpp GGUF (Llama-3.1 8B Q4_K_M), 35 GPU layers, ~4.4 GB VRAM, loads in seconds via the `ModelManager` singleton.
- **`.imn` read/write** with file locking ([imn-format.md](../backend/imn-format.md)).
- **ComfyUI plumbing.** The `engram_comfy` harness submits workflows to ComfyUI `:8188`; the agents correctly build, submit, and record results/failures.
- **Progress streaming.** Broker → WS → React hook is wired end-to-end ([progress-streaming.md](../architecture/progress-streaming.md)).
- **Flux GGUF image generation** is proven runnable locally on the 4080 (prior session) — just not yet wired as the pipeline's image workflow.

## What's broken / blocked

Priority order:

1. **Image generation fails — ComfyUI has no SDXL-Turbo checkpoint** (`value_not_in_list: ckpt_name 'sd_xl_turbo_1.0_fp16.safetensors' not in []`). The checkpoint list is empty; the verified Flux work used a GGUF UNet loader, not `CheckpointLoaderSimple`. **Decision needed:** (a) register `sd_xl_turbo_1.0_fp16.safetensors` in ComfyUI's checkpoints path, or (b) leapfrog to a Flux workflow (`scene_image_flux_krea.json`) since Flux is already proven. Option (b) aligns with the roadmap. Until fixed, video is also skipped (it needs the image as input).
2. **API response is all-null.** `POST /api/dream` returns `{dream_name: null, ...}` because the handler reads `result.get("dream_name")` from the LangGraph `state`, but Carthir writes those into `carthir_memory`/the `.imn`, not top-level state. The data exists in the file; the response just doesn't surface it.
3. **`.imn` path mismatch.** Agents write `Backend/Dreams/`; `api_server` `get_dream` reads `Backend/Python/Backend/Dreams/`. `GET /api/dreams/{id}` 404s for freshly created dreams. Pick one directory.

### Fixed this session (2026-05-23)
- **GPU OOM segfault.** `ModelManager.preload_for_pipeline()` was loading the unused in-process diffusers SDXL pipelines into VRAM on top of llama-cpp + ComfyUI → native crash (exit 139), and downloading SDXL-base (~7 GB). Now preloads **only the LLM** (`core/model_manager.py`).
- **`UnicodeEncodeError` on emoji prints.** Windows cp1252 stdout can't encode the `✅`/`🎬` in `print()` calls → 500. Worked around at launch with `PYTHONIOENCODING=utf-8` + `PYTHONUTF8=1`. A code-side fix (reconfigure stdout, or drop emoji) would make it launch-agnostic.

## What can be removed / is legacy

- **In-process diffusers image path** — `core/image_generator.py` and the SDXL pipelines in `core/model_manager._load_image_models()` (`get_sdxl_turbo`/`get_sdxl_lora`). Used **only** by `test_gui.py`; the real pipeline goes through ComfyUI. Candidate for deletion once `test_gui.py` is migrated to the ComfyUI path. Removing it also lets `ModelManager` drop its `torch`/`diffusers` imports.
- **`Backend/Python/Wan2.2` submodule** — legacy in-process video; visual gen runs through ComfyUI. Defer removal until production usage validated (per CLAUDE.md known issues).
- **Empty `Backend/Python/.venv`** — has no deps; misleading. Either populate it from `requirements.txt` or remove it so people use the global interpreter knowingly.
- **Stale `.imn` corpora** in both `Backend/Dreams/` and `Backend/Python/Backend/Dreams/` — old test output, mixed schema versions. Safe to prune once the path mismatch (#3 above) is resolved.
- **README.md drift** — still describes the old in-process diffusers world, SDXL-Turbo as current, "four agents," sub-10s claims. CLAUDE.md + this wiki are authoritative; the README needs a pass.
- **"Parallel" framing** — `pipeline_instance.py` docstring and commit history say "native parallelization," but the graph is strictly sequential. Either implement parallel edges or correct the language.

## What's next (roadmap)

From [`CLAUDE.md`](../../CLAUDE.md) "Model upgrade direction", in impact order:

1. **Unblock image** — wire a working image workflow (Flux Krea Dev preferred; SDXL-Turbo as fast/draft path). Biggest visible win.
2. **T5 optimization** — `t5xxl_fp16` → `t5xxl_fp8_e4m3fn` or T5 GGUF; cuts the ~51 s warm-new-prompt Flux cost (T5 is the bottleneck, not the UNET).
3. **Aspect ratio** — make `state["aspect_ratio"]` first-class, default new dreams to **9:16**, parameterize workflow dimensions.
4. **Video** — evaluate **Wan 2.6 Reference-to-Video** for style-cloning from reference clips; verify it runs on the 4080. Add `pre_production.reference_clips` to `.imn`.
5. **LoRA** — confirm `scene_image_sdxl_lora.json`, then build a Flux Krea LoRA for persona/character style locking.

Out of scope for now: campaign/long-form mode, Llama LLM swap, local audio generation.

## Commit status

As of 2026-05-23 the WebSocket-progress + model-manager work (`agents.py`, `api_server.py`, `pipeline_instance.py`, `progress_broker.py`, `model_manager.py`, etc.) is **uncommitted on `main`**. The narrative half is now validated end-to-end; the image half is blocked on the ComfyUI checkpoint decision. Recommend committing the narrative pipeline + the two crash fixes once the image path is decided.
