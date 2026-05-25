---
title: Summaries
status: canonical
last_reviewed: 2026-05-23
related: [_index.md]
---

# Summaries

One-paragraph blurb per article for fast lookup. Read [`_index.md`](_index.md) for the navigable topic tree.

## architecture/overview.md
What Dreams.ai is and how the pieces fit: React frontend → FastAPI (`:8000`) → an in-process LangGraph pipeline that runs narrative agents on a local Llama-3.1 8B (llama-cpp) then visual agents that call a separate ComfyUI process (`:8188`). Covers the request lifecycle, the two entry points (FastAPI vs the Flask `test_gui`), and the VRAM constraint (16 GB 4080 shared with Valinor) that forbids loading in-process diffusers alongside llama-cpp + ComfyUI.

## architecture/pipeline.md
The LangGraph `StateGraph`: a strictly **sequential** graph where every node returns to `CarthirSupervisor`, which advances a `pipeline_step` and routes onward. Documents each agent (Carthir, convert_prompt, Narnion, CarthirReview, Cenedril, CenedrilImageGenerator, CenedrilVideoGenerator), what it reads/writes, the shared `State`, failure handling (visual agents record failures and continue), and the verified 2026-05-23 run. Includes the three runtime gotchas (LLM-only preload, UTF-8 stdout, `.imn` path mismatch).

## architecture/visual-generation.md
How images/video are made: the `engram_comfy` harness (`COMFY_TRANSPORT=direct`) submits workflow JSONs to ComfyUI. Lists the workflows (SDXL-Turbo default, SDXL-LoRA, LTX-Video, Wan2.2) and their loaders, where models live, what's proven (Flux GGUF) vs broken (SDXL-Turbo checkpoint not registered), performance numbers, and the upgrade roadmap.

## architecture/progress-streaming.md
The per-dream WebSocket progress system: `core/progress_broker.py` (thread-safe in-process pubsub) bridges the LangGraph worker thread to the asyncio WS handler in `api_server.py`, which forwards events (with heartbeats) to the React `useDreamProgress` hook. Documents the event shape and the close logic. Note: only the visual agents publish; the ~11 s narrative phase is silent.

## backend/imn-format.md
The `.imn` JSON file — the single shared state document threaded through every agent. Three sections: `pre_production` (Carthir/Review/Cenedril narrative + the `cenedril_shot_composition` prompt), `in_production` (Narnion scenes with 3 actions each), `post_production` (comfy image/video results). Covers file locations and the write-vs-read path mismatch, plus schema drift vs the README.

## operations/testing.md
The verified way to run it: ComfyUI on `:8188`, then the global Python 3.13.5 (not the empty `.venv`) running uvicorn with `PYTHONIOENCODING=utf-8`. The Flask GUI alternative. A ComfyUI smoke test. A table of environment gotchas (empty venv, OOM segfault, emoji crash, triton noise, missing checkpoint) with fixes.

## operations/status-and-roadmap.md
The living status doc: what works (full narrative pipeline, ~11.6 s), what's broken (image gen blocked on missing SDXL-Turbo checkpoint; null API response; `.imn` path mismatch), what was fixed 2026-05-23 (OOM preload, UTF-8 crash), what's removable (in-process diffusers path, Wan2.2 submodule, empty venv, stale `.imn` sets, README drift), and the prioritized roadmap (unblock image → T5 fp8 → 9:16 aspect → Wan 2.6 → LoRA).
