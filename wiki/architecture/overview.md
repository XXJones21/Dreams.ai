---
title: Architecture Overview
status: canonical
last_reviewed: 2026-05-23
related:
  - architecture/pipeline.md
  - architecture/visual-generation.md
  - architecture/progress-streaming.md
  - backend/imn-format.md
sources:
  - Backend/Python/api_server.py
  - Backend/Python/core/pipeline_instance.py
  - CLAUDE.md
---

# Architecture Overview

Dreams.ai turns a text prompt into an interactive, illustrated "dream." Everything runs locally: the narrative LLM, image diffusion, and video synthesis all execute on-device. The product target is **portrait 9:16, first-person, dark/dreamlike short-form video**.

## The three layers

```
+-------------------+      POST /api/dream            +------------------------+
|  React Frontend   | ------------------------------> |  FastAPI (api_server)  |
|  (Vite + TS)      |  ws /api/dream/:id/progress     |  :8000                 |
+-------------------+ <-----------------------------> +-----------+------------+
                                                                  |
                                                                  | PipelineInstance.run()
                                                                  v
                                              +-----------------------------------+
                                              |  LangGraph pipeline (in-process)  |
                                              |  Carthir → Narnion → Review →     |
                                              |  Cenedril → Image → Video         |
                                              +--------+-----------+--------------+
                                                       |           |
                                  narrative (Llama-3.1 8B)     visual (engram_comfy)
                                                       |           |
                                                       v           v
                                          llama-cpp (GGUF)     ComfyUI :8188
                                          35 GPU layers        SDXL-Turbo / LTX / Wan2.2
```

| Layer | Stack | Where |
| --- | --- | --- |
| Frontend | Vite + React + TypeScript, Tailwind, React Router, Supabase | `src/` |
| API | FastAPI + uvicorn (`:8000`); Flask GUI alt (`test_gui.py`, `:5000`) | `Backend/Python/api_server.py` |
| Narrative | LangGraph StateGraph + `llama-cpp-python` (Llama-3.1 8B Q4_K_M GGUF) | `Backend/Python/core/agents.py` |
| Visual | ComfyUI fronted by the `engram_comfy` harness | external `:8188` |
| Storage | `.imn` JSON dream files + Supabase | `Backend/Dreams/*.imn` |

## Request lifecycle

1. Frontend `POST /api/dream {prompt}`. The handler builds a `state` dict (`id`, `messages`, `generate_video=True`, `video_cinematic=False`) and constructs a [`PipelineInstance`](pipeline.md).
2. `PipelineInstance.__init__` **preloads the narrative LLM** (see note below), then compiles the LangGraph workflow.
3. `pipeline.run()` is dispatched off the event loop via `asyncio.to_thread` so the WebSocket progress endpoint stays responsive.
4. Agents read/write a shared [`.imn` file](../backend/imn-format.md) as they run; visual agents `publish()` progress events.
5. The handler returns a small JSON summary; the frontend has already been streaming live progress over [WebSocket](progress-streaming.md).

## GPU reality (RTX 4080, 16 GB, shared with Valinor)

VRAM is the binding constraint and shapes the whole design:

- The narrative LLM loads in-process via llama-cpp with **35 GPU layers** (~4.4 GB).
- Image/video generation runs in a **separate ComfyUI process** on `:8188` that also holds models.
- **Do not also load the legacy in-process diffusers SDXL pipelines** — doing so OOM-segfaults the GPU. This was an active bug; see [operations/status-and-roadmap.md](../operations/status-and-roadmap.md).

## Two entry points

| Entry | Process | Visual path | Video? |
| --- | --- | --- | --- |
| `api_server.py` (`uvicorn`, `:8000`) | FastAPI + WS progress | ComfyUI via `engram_comfy` | Yes (`generate_video=True` default) |
| `test_gui.py` (Flask, `:5000`) | Visual GUI test harness | historically in-process diffusers (`core/image_generator.py`); also has ComfyUI path | image-only by default |

Both set `COMFY_TRANSPORT=direct` at import so the harness talks straight to ComfyUI on `:8188`.

## Where to go next

- [architecture/pipeline.md](pipeline.md) — the agent graph and supervisor routing.
- [architecture/visual-generation.md](visual-generation.md) — ComfyUI, `engram_comfy`, workflows, models.
- [architecture/progress-streaming.md](progress-streaming.md) — the WS progress system.
- [backend/imn-format.md](../backend/imn-format.md) — the state file.
