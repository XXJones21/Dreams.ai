---
title: Testing & Running
status: canonical
last_reviewed: 2026-05-23
related:
  - operations/status-and-roadmap.md
  - architecture/overview.md
sources:
  - TESTING.md
  - README.md
  - Backend/Python/api_server.py
---

# Testing & Running

The canonical run guide is the repo root [`TESTING.md`](../../TESTING.md). This article captures the **verified** invocation and the environment gotchas discovered on 2026-05-23.

## Prerequisite: ComfyUI on `:8188`

Image/video need a local ComfyUI with the right models. The verified install is `D:\Tools\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable`; launch with `run_nvidia_gpu_fast_fp16_accumulation.bat`. Confirm it's up:

```powershell
(Invoke-WebRequest http://127.0.0.1:8188/system_stats -UseBasicParsing).StatusCode  # expect 200
```

> ⚠️ The SDXL-Turbo checkpoint is **not currently registered** in that ComfyUI (checkpoint list is empty), so the default image workflow fails. Flux GGUF is the proven path. See [status-and-roadmap.md](status-and-roadmap.md).

## The two run modes

### FastAPI + WebSocket (full image + video, live progress)

This is the path verified end-to-end. Use the **global** Python 3.13.5 interpreter — it has the deps (`uvicorn`, `fastapi`, `langgraph`, editable `engram_comfy`). The repo's `Backend/Python/.venv` is empty; do **not** use it.

```powershell
cd D:\Dreams.ai\Backend\Python
$env:PYTHONIOENCODING="utf-8"; $env:PYTHONUTF8="1"   # REQUIRED: emoji prints crash on cp1252
python -m uvicorn api_server:app --host 127.0.0.1 --port 8000
```

Fire a dream (defaults `generate_video=True`):

```powershell
curl.exe -s -X POST http://127.0.0.1:8000/api/dream `
  -H "content-type: application/json" `
  -d '{\"prompt\":\"You stumble upon an enchanted forest where magical mushrooms glow with an ethereal light.\"}'
```

The narrative `.imn` lands in `Backend/Dreams/<id>.imn`. The HTTP response is currently all-null (a known API-surface bug — the data is in the file, not the response).

Frontend: `npm run dev` (Vite on `:5173`), which subscribes to `ws://localhost:8000/api/dream/<id>/progress`.

### Flask GUI (`test_gui.py`, image-only)

```powershell
.\start_gui_test.ps1     # serves http://localhost:5000
```

Image-only by default; uses the legacy in-process diffusers path (`core/image_generator.py`). Edit `run_pipeline_test` to flip video on.

## ComfyUI image smoke test (bypasses Dreams.ai)

```powershell
curl.exe -X POST http://127.0.0.1:8188/prompt -H "Content-Type: application/json" --data "@flux_gguf_smoketest.json"
# poll http://127.0.0.1:8188/history/<prompt_id>; output in ComfyUI/output/
```

## Environment gotchas (learned the hard way)

| Symptom | Cause | Fix |
| --- | --- | --- |
| `No module named uvicorn` | empty `Backend/Python/.venv` | use the global Python 3.13.5 |
| Process exits 139 (segfault) mid-request | diffusers SDXL preload OOMs the 16 GB GPU | preload only the LLM (already fixed in `model_manager.py`) |
| HTTP 500, `UnicodeEncodeError '✅'` | emoji `print()` on cp1252 stdout | `PYTHONIOENCODING=utf-8` + `PYTHONUTF8=1` |
| `No module named 'triton'` | xformers probing for triton at import | harmless — ignore |
| image `value_not_in_list: ckpt_name` | ComfyUI has no SDXL-Turbo checkpoint | register SDXL-Turbo, or switch workflow to Flux GGUF |
