# Dreams.ai — How to Test

Two entry points cover everything. Pick the one that matches what you want to look at.

| Entry point | What you get | When to use |
|---|---|---|
| **`start_gui_test.ps1`** (Flask on :5000) | Standalone GUI with dream cards, debug logs, performance breakdown. Runs the full LangGraph pipeline (Carthir → Narnion → Review → Cenedril → CenedrilImage → CenedrilVideo) per request. | Day-to-day pipeline smoke testing. Your normal flow. |
| **`uvicorn api_server:app`** (FastAPI on :8000) + Vite (5173) | Production-shaped surface: REST `POST /api/dream`, live `WS /api/dream/:id/progress`, React `DreamDetailPage` rendering image + video inline. | E2E flow as the real frontend would see it. |

Both paths run through the **same** `PipelineInstance` and the **same** engram_comfy → ComfyUI flow under the hood. The GUI just wraps the result in extra debug instrumentation.

---

## 0. Prerequisites (one-time)

You need ComfyUI running on `127.0.0.1:8188` with the image stack (Flux Q4 GGUF + clip_l + t5xxl + 16-ch Flux VAE) and the `ComfyUI-LTXVideo` + `ComfyUI-GGUF` + `ComfyUI-KJNodes` custom nodes installed.

**Video (default `scene_video_ltx2` = LTX-2.3 GGUF, verified on a 16 GB 4080):** put these in `ComfyUI/models/` — `unet/ltx-2.3-22b-dev-Q3_K_S.gguf`, `text_encoders/{gemma-3-12b-it-Q4_K_M.gguf, ltx-2.3-22b-dev_embeddings_connectors.safetensors}`, `vae/{ltx-2.3-22b-dev_video_vae.safetensors, ltx-2.3-22b-dev_audio_vae.safetensors}`, `loras/ltx-2.3-22b-distilled-lora-384.safetensors`, `latent_upscale_models/ltx-2.3-spatial-upscaler-x2-1.0.safetensors` (all from `unsloth/LTX-2.3-GGUF` + `unsloth/gemma-3-12b-it-qat-GGUF`). **Two gotchas or you get pure noise:** (1) apply the `pad = F.pad` shim in `ComfyUI-LTXVideo/pyramid_blending.py` (kornia 0.8.3 lacks `pad`, else the whole pack fails to import); (2) the workflow uses `DualCLIPLoaderGGUF` with clip2 = the **embeddings_connectors** file (not text_projection). A ~5 s clip takes ~4.4 min, ~10 s ~7.6 min.

Step-by-step (Windows, reuses your existing portable install):

> **`D:\Tools\personalAI\Engram\Resources\engram_comfy\bootstrap\README.md`**

The bootstrap README also drops a `extra_model_paths.yaml` into your ComfyUI install so the diffusers-format weights already under `Backend/Python/models/` are visible to ComfyUI without copies.

Sanity check before going further:

```powershell
# In a separate shell, ComfyUI launched and idle:
curl http://127.0.0.1:8188/system_stats
# Should return JSON with system / device info.
```

Also confirm the `engram_comfy` import works from the Dreams.ai venv:

```powershell
cd D:\Dreams.ai\Backend\Python
.venv\Scripts\activate
python -c "from engram_comfy import ComfyImageGenerator; print('ok')"
```

If you see `ok`, the harness is reachable.

---

## 1. GUI flow (your normal path)

```powershell
# From the repo root:
.\start_gui_test.ps1
```

What this does:

1. `cd Backend\Python` and launches `python test_gui.py` (Flask).
2. Sets `COMFY_TRANSPORT=direct` so the pipeline talks to your local ComfyUI on :8188.
3. Opens `http://localhost:5000` — paste a prompt, click run, watch the dream card populate.

Behind each "run pipeline test" click:

- `PipelineInstance(state).run()` executes the LangGraph workflow.
- `CenedrilImageGenerator` submits the SDXL-Turbo workflow via `engram_comfy`, writes the result to `post_production.image_generation` in the IMN, and Cenedril sets the latest scene's `frame_image`.
- `CenedrilVideoGenerator` runs if `state["generate_video"]` is set — *the GUI does NOT set this by default*, so by default you get image only. (To exercise video here, edit `test_gui.py::run_pipeline_test` and add `"generate_video": True` to `test_state`.)
- The GUI then also calls `generate_dream_image` directly (legacy in-process SDXL path) for backwards compatibility with the dream-card UI. This is **redundant** with the ComfyUI generation above — both are run today. Safe to delete that block once we're confident in ComfyUI; tracked as a follow-up.

Check the result:

- `D:\Dreams.ai\Backend\Dreams\<dream_id>.imn` — open it; `post_production.image_generation` should have `service: "comfy"`, an `asset_url`, and the SDXL-Turbo filename.
- `D:\Tools\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\ComfyUI\output\engram_scene_*.png` — the actual file ComfyUI saved.

If `post_production.image_generation` shows `status: "failed"` or `"skipped"`, see Troubleshooting below.

---

## 2. FastAPI + React flow (full UX, includes video)

Three processes, one in each shell.

**Shell 1 — ComfyUI** (already running from prereqs):

```powershell
cd D:\Tools\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\ComfyUI
..\python_embeded\python.exe main.py --listen 127.0.0.1 --port 8188
```

**Shell 2 — Dreams.ai backend:**

```powershell
cd D:\Dreams.ai\Backend\Python
.venv\Scripts\activate
uvicorn api_server:app --host 127.0.0.1 --port 8000 --reload
```

`api_server.py` boots with `COMFY_TRANSPORT=direct` and `generate_video=True` baked into every `/api/dream` request (MVP default). Override via env if you want video off, or flip the API to gate it explicitly (see TESTING.md "WP-F" notes).

**Shell 3 — Vite dev server:**

```powershell
cd D:\Dreams.ai
npm run dev
```

Vite serves the React app on `http://localhost:5173` (CORS is already loosened in `api_server.py` to include this origin).

End-to-end check:

```powershell
# Shell 4 — fire a request:
curl.exe -X POST http://localhost:8000/api/dream `
  -H "content-type: application/json" `
  -d '{\"prompt\":\"A lighthouse keeper finds a message in a bottle\"}'
```

The response carries `id`. In the browser, navigate to `http://localhost:5173/dream/<id>`:

- `DreamDetailPage` opens `ws://localhost:8000/api/dream/<id>/progress` and streams Cenedril image/video stages live.
- When the image stage publishes `stage: "completed"`, the still appears inline.
- When the video stage publishes `stage: "completed"`, the `<video>` player appears below.

Manual WS spy (no React):

```powershell
npx wscat -c ws://localhost:8000/api/dream/<id>/progress
```

You should see events like:

```json
{"stage":"submit","kind":"image","workflow":"scene_image_sdxl_turbo"}
{"stage":"completed","kind":"image","asset_url":"http://127.0.0.1:8188/view?filename=engram_scene_00001_.png"}
{"stage":"submit","kind":"video","workflow":"scene_video_ltx2"}
{"stage":"completed","kind":"video","asset_url":"http://127.0.0.1:8188/view?filename=engram_video_00001_.webp"}
```

---

## 3. Troubleshooting

**`[CenedrilImage] engram_comfy not installed, skipping image generation`**
The Dreams.ai venv doesn't have the package. Run:
```powershell
cd D:\Dreams.ai\Backend\Python
.venv\Scripts\activate
pip install -r requirements.txt
```
The `requirements.txt` includes `-e D:/Tools/personalAI/Engram/Resources/engram_comfy`.

**`post_production.image_generation.status == "failed"` in the IMN**
- Most often: ComfyUI isn't running, or the workflow's `ckpt_name` doesn't match a checkpoint you downloaded. Check the ComfyUI shell — every `/prompt` POST logs.
- Workflow files live at `D:\Tools\personalAI\Engram\Resources\engram_comfy\engram_comfy\workflows\*.json`. Open `scene_image_sdxl_turbo.json` and confirm the `ckpt_name` field matches your SDXL-Turbo filename in `ComfyUI\models\checkpoints\`.

**`ImportError: numpy.dtype size changed`** (or similar ABI error during pipeline boot)
The Dreams.ai venv was bumped to numpy 2.x when `engram_comfy` was installed and one of the heavy deps (likely `llama-cpp-python` or a transformers dep) was built against numpy 1.x. Pin numpy down:
```powershell
pip install "numpy<2"
```
…then reinstall the offending wheel.

**`from main import graph` ImportError**
Fixed — `api_server.py` now constructs `PipelineInstance` per request. If you see this error, you're running an old copy of `api_server.py`. Pull latest.

**Browser console shows CORS errors**
`api_server.py` allows `http://localhost:5173` and `http://127.0.0.1:5173`. If your Vite dev server runs on a different port, add it to the `allow_origins` list.

**Video stage never fires**
Confirm `state["generate_video"]` is `True` in the request that reached `CarthirSupervisor` (look at the agent log lines). `api_server.py` sets it; `test_gui.py` does not by default.

**`outetts requires llama-cpp-python==0.3.9` and other dep conflicts shown during pip install**
Pre-existing in this venv. Not on the MVP path (those packages aren't imported by the ComfyUI flow). Ignore unless an actual `ImportError` shows up at runtime.

---

## 4. What's intentionally not in this guide

- Frontend production build / Netlify deploy — see `README.md`.
- Rust supervisor (`valinor-server/comfyui.rs`) — MVP uses direct transport. To flip:
  ```
  set COMFY_TRANSPORT=rust
  set COMFY_BASE_URL=http://127.0.0.1:8765
  ```
  …and start the Rust binary with ComfyUI managed under it. See `Engram/Projects/valinor/deep-agent-server/claude.md`.
- Wan2.2 cinematic video path — kept as `scene_video_wan22.json` workflow, enabled by passing `video_cinematic: True` in state. Defer until LTX baseline is solid.
