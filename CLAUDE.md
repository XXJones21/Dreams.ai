# Dreams.ai

Interactive storytelling platform with AI-driven narrative generation and visual content. Local-first: narrative LLM, image diffusion, and video synthesis all run on-device via ComfyUI. The current focus is producing **portrait, first-person, dark/dreamlike short-form video** — see "Aesthetic North Star" below.

## Tech Stack

- **Frontend:** Vite + React + TypeScript, Tailwind CSS, React Router, Supabase
- **Backend:** Python 3.13+, LangChain/LangGraph, llama-cpp-python (GGUF), PyTorch, diffusers/transformers
- **Visual generation:** ComfyUI (image + video), fronted by Valinor's Rust supervisor at `127.0.0.1:8765/comfy/*`
- **Storage:** `.imn` dream files (JSON), Supabase

## Architecture

LangGraph pipeline of narrative agents then visual agents:

```
Carthir → Narnion → CarthirReview → Cenedril → CenedrilImageGenerator → CenedrilVideoGenerator
[--------------- narrative (Llama-3.1 8B) ---------------]   [-------- ComfyUI visual --------]
```

- **Cenedril** (`core/agents.py`) authors the SDXL/Flux shot-composition prompt → writes `pre_production.cenedril_shot_composition`.
- **CenedrilImageGenerator** reads that prompt, calls `engram_comfy.ComfyImageGenerator(...).generate_image(...)`, writes result to `post_production.image_generation`.
- **CenedrilVideoGenerator** runs only when `state["generate_video"]` is set; default workflow is **`scene_video_ltx2`** (LTX-2.3 GGUF two-stage text-to-video, portrait 9:16, verified on the 4080 ~4–5 min); `state["video_cinematic"]` selects Wan2.2. It's text-to-video off the Cenedril shot prompt (the passed `image_input` is harmlessly ignored — true I2V from the generated frame is a future enhancement). **Working LTX-2.3 GGUF recipe & gotchas: see Engram/memory and the `scene_video_ltx2.json` `_meta.notes` — the critical one is `DualCLIPLoaderGGUF` clip2 = `ltx-2.3-22b-dev_embeddings_connectors.safetensors` (NOT text_projection), and the pack needs the `pad = F.pad` shim in `ComfyUI-LTXVideo/pyramid_blending.py` to load at all.**
- **Progress** streams over WebSocket: `core/progress_broker.py` (thread-safe pubsub) → FastAPI WS handler in `api_server.py` → React hook `src/hooks/useDreamProgress.ts`.

### `.imn` post_production schema
- `image_generation`: `{ service: "comfy", status, workflow, prompt, prompt_id, seed, asset_url, filename, filepath, generated_at, model }`
- `video_generation`: parallel block when the video stage runs
- Latest scene's `frame_image` gets the image asset URL written back automatically.

## How to test

`TESTING.md` is canonical. TL;DR:
1. Start ComfyUI on `:8188` (see "Local inference setup" below).
2. Either `.\start_gui_test.ps1` (Flask GUI, image-only by default) **or** `uvicorn api_server:app --port 8000` + Vite (full image + video over WS).
3. `api_server.py` POST `/api/dream` defaults `generate_video=True`; `test_gui.py` does not (image-only — edit `run_pipeline_test` to flip).

ComfyUI image-only smoke test (bypasses Dreams.ai, confirms the GPU stack):
```bash
curl -X POST http://127.0.0.1:8188/prompt -H "Content-Type: application/json" --data @flux_gguf_smoketest.json
# poll http://127.0.0.1:8188/history/<prompt_id>; output lands in ComfyUI/output/
```

## Local inference setup (verified 2026-05-23)

ComfyUI install used for testing: `D:\Tools\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable`. Hardware: **RTX 4080, 16 GB VRAM**, shared with Valinor.

- **Launch with** `run_nvidia_gpu_fast_fp16_accumulation.bat` (adds `--fast fp16_accumulation` → ~10–25% faster sampling on Ada, requires torch ≥ 2.7).
- **torch must be CUDA-built.** Current working: `torch 2.11.0+cu128`. ComfyUI's `update_comfyui_and_python_dependencies.bat` re-pulls **CPU-only** torch from PyPI and breaks CUDA. Fix:
  ```
  python_embeded\python.exe -s -m pip install --force-reinstall torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
  ```
- **Verified working image stack:** Flux1-dev **Q4_K_S GGUF** (6.4 GB) via the `ComfyUI-GGUF` custom node (`UnetLoaderGGUF`), `clip_l` + `t5xxl_fp16` text encoders, and the **16-channel Flux VAE** (`flux_vae.safetensors`, sourced from the FLUX.1-dev diffusers cache — NOT Dreamwave's `ae.safetensors`, which is a mislabeled 4-channel SD VAE and will fail VAEDecode).
- **Models live in** `D:\Dreams.ai\Backend\Python\models\` (HF diffusers caches: FLUX.1-dev/schnell, LTX-Video, SVD; flat Wan2.2 transformer; single-file `flux1-dev-Q4_K_S.gguf` and the Llama GGUF), exposed to ComfyUI via `extra_model_paths.yaml`.

### Benchmark (RTX 4080, Flux Q4 GGUF, 20 steps, 768×1344 portrait)
| Run | Notes | Time |
|---|---|---|
| Cold (model load) | first generation | ~64 s |
| Warm, same prompt | conditioning + weights resident | ~16 s |
| Warm, **new prompt** | fresh T5 encode | **~51 s** |

**Bottleneck = the T5 text encoder, not the UNET.** `t5xxl_fp16` is 9.2 GB; with ~10 GB RAM free it gets evicted between runs, so every new prompt pays a cold T5 cost. Since the narrative agents change the prompt every scene, real-world per-image cost is ~50 s. **Highest-value optimization: swap `t5xxl_fp16` → `t5xxl_fp8_e4m3fn` (~4.9 GB) or a T5 GGUF** so it stays resident.

## Aesthetic North Star

Target output = portrait **9:16**, **first-person POV**, dark/dreamlike short-form (YT Shorts / Reels / TikTok). Reference creators:
- **The Archive In Between** — https://www.youtube.com/shorts/Vv5BrF-gVuc ("digital illustration + AI image creation, words by a human"). Curated dream-archive tone.
- **Gloomstomper / @voidstomper** — https://www.youtube.com/shorts/Xbzbo3zeNAk. AI-horrorcore; confirmed to train a custom face-LoRA; "embrace the AI glitch." 3M IG followers.

These creators stitch SaaS tools (Kling, Veo, Runway, Midjourney, Nano Banana). Dreams.ai's job is to reach the same caliber **locally** via OSS models. Their technique is mostly post-production discipline (locked reference boards, post-grade defects, wide-lens first-person framing, flashlight-driven lighting) — reproducible in our pipeline if it supports reference boards + portrait + a post-process pass.

## Model upgrade direction (research 2026-05-23)

Full survey in Engram: `D:\Tools\personalAI\Engram\Resources\comfy_model_survey_2026-05-23.md`. Prioritized levers (image change is the biggest aesthetic jump; current image model SDXL-Turbo is ~30 months old):

1. **Image:** SDXL-Turbo → **Flux.1 Krea Dev** (proven Flux runs locally — see benchmark). Keep SDXL-Turbo as a draft/fast path.
2. **Video:** Wan 2.2 → **Wan 2.6 Reference-to-Video** (ComfyUI-native since Jan 2026; ingests up to 2 reference clips to clone motion/camera/style — the lever for matching the reference shorts). Verify local-runnable on the 4080.
3. **Aspect ratio:** make `state["aspect_ratio"]` first-class; default new dreams to **9:16**; parameterize ComfyUI workflow dimensions.
4. **Reference clips:** add `pre_production.reference_clips` to `.imn` for Wan 2.6 to consume.
5. **LoRA:** confirm `scene_image_sdxl_lora.json` works; build a Flux Krea LoRA variant for persona/character style locking.

Out of scope for now: campaign mode (long-form interactive film), Llama LLM swap, local audio generation.

## Interactive video direction — gesture-driven segmentation (planned)

Design doc: **`docs/interactive-video-segmentation-pipeline.pdf`**. This is the target interactive experience the **end-to-end pipeline test should exercise**, and where Dreams is heading beyond linear dream playback.

**Concept (not pre-authored branching):** a user pauses a playing video, **taps an object** in the frame, and gives a **natural-language instruction** ("open the door"). The system identifies the *specific* tapped instance (even with multiple of the same class in frame), then generates a **continuation video** where that object responds. Outcomes are dynamic, driven by user intent.

**Pipeline** (inputs: `frame_N` paused frame, tap `(x,y)`, `instruction`):
1. **Parse instruction** → target noun + action verb via a small/fast LLM (~100 ms). e.g. `target="door"`, `action="open"`.
2. **Segment with SAM 3** — `frame_N` + point prompt `(x,y)` + concept prompt `"door"`. SAM 3's Promptable Concept Segmentation makes the concept native to the seg call, solving multi-instance disambiguation in **one** model call (no separate VLM "what is this" pass SAM 2 would need). Binary mask, hosted GPU ~100–300 ms. (Meta, 2025-11-19, open SAM license; 848M params: shared vision encoder → DETR detector + SAM2-derived tracker.)
3. **Build payload:** `frame_N` = first-frame I2V conditioning; `mask` = spatial control (ROI / inpaint / ControlNet-style); `action` = motion text prompt.
4. **Generate continuation** — I2V model with **regional/mask conditioning** (the latency bottleneck, seconds–tens). Hide with **diegetic pacing** (darkness, sound, camera push-in) — the dark/dreamlike north-star aesthetic is forgiving here.
5. **Stitch:** `frame_N` is the last frame of clip A and first of clip B → invisible transition if the model respects the conditioning.

**UX principle (Apple Subject Lifting):** *decouple acknowledgment from resolution* — show the user you heard them before you're done thinking. Staggered tiers: Instant <100 ms (tap shimmer) · Fast 200–800 ms (mask + parse, object outlined) · Slow seconds+ (generation, pacing beat).

**How it maps to Dreams today:** step 4 is exactly the **LTX-2.3 GGUF I2V video stage** now working, and `CenedrilImageGenerator`'s frame is the natural `frame_N`. The **new requirement is mask/regional conditioning** — LTX-2.3 ships IC-LoRA control workflows (`LTX-2.3_ICLoRA_Union_Control_Distilled`, etc.) as the local path. New pieces: SAM 3 segmentation + the tap/instruction-parse step (the existing Llama can absorb the parse). **Next steps:** prototype SAM 3 seg in isolation (tap+concept on a multi-door set); pick the I2V model with best mask conditioning; build the staggered-feedback UX shell.

## Conventions

- `engram_comfy` is `pip install -e`'d via `Backend/Python/requirements.txt`; uses `COMFY_TRANSPORT=direct` (set by `api_server.py` and `test_gui.py` at module load).
- ComfyUI workflow JSONs live in the `engram_comfy` package: `scene_image_sdxl_turbo.json`, `scene_image_sdxl_lora.json`, `scene_video_ltx.json`, `scene_video_wan22.json`.
- This repo is local + Supabase. Engram (the cross-session brain) is at `D:\Tools\personalAI\Engram`; project context there is `Projects/dreams-ai/claude.md`.

## Known issues

- API server CORS hardcoded to a Netlify URL; needs env-driven config for local dev.
- `Backend/Python/Wan2.2` submodule and in-process `diffusers` code in `core/image_generator.py` are legacy paths — visual gen runs through ComfyUI. Defer removal until production usage is validated.
- Cenedril's strict perspective validation can fail noisily on edge cases; image generation step doesn't run if Cenedril raises. Worth a tolerance pass once telemetry shows where it triggers.
- **Uncommitted work on `main` as of 2026-05-23** (model_manager, progress_broker, agents, api_server, pipeline_instance, etc.) — yesterday's updates, not yet committed or end-to-end tested through the full Dreams.ai pipeline.
