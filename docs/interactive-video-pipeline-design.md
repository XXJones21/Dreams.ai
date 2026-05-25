# Interactive Video Pipeline — Design (v1 backend E2E)

> Design for the gesture-driven interactive video experience. Source brief: [`interactive-video-segmentation-pipeline.pdf`](./interactive-video-segmentation-pipeline.pdf). Drafted 2026-05-25.

## Goal

Evolve Dreams from one-shot linear dream generation into a **runtime interaction loop**: a user pauses a playing video, **taps an object**, gives a **natural-language instruction** ("open the door"), and the system generates a **continuation** where *that specific object* responds. A dream becomes a **branching tree of clips** driven by user intent — not pre-authored branching.

## Decisions (locked)

1. **First E2E = backend loop only** (script/test-driven, no UI). Prove `parse → segment → generate → stitch` before building the React interaction shell.
2. **SAM 3 = hosted endpoint** for v1 (no GPU contention with LTX on the 16 GB 4080; per-call cost acceptable). Self-host later if usage scales.
3. **Mask conditioning = LTX region/inpaint masking, NOT union-control IC-LoRA.**
   - *Why the change from the initial "verify IC-LoRA control" pick:* the Lightricks IC-LoRA repos are gated (401), union-control is built for **structural** control (depth/canny/pose) whose preprocessor nodes we don't have, and it needs a download. Meanwhile LTX's **region/inpaint-mask nodes are already installed** (`LTXVSetVideoLatentNoiseMasks`, `LTXVInpaintPreprocess`, `LTXVAddLatentGuide`, `SetLatentNoiseMask`, `InpaintModelConditioning`) and are the natural fit for "the tapped object responds." **Zero downloads.**

## Current state (what we build on)

- One-shot `StateGraph` (`Backend/Python/core/pipeline_instance.py`): `POST /api/dream` → supervisor routes `narnion → carthir_review → cenedril → cenedril_image → cenedril_video` → writes one `.imn` (narrative + image + video) → WS streams progress.
- **Video stage works:** `scene_video_ltx2` (LTX-2.3 GGUF, two-stage, 8-step, portrait 9:16, POV-locked) via ComfyLocalMCP `ComfyVideoGenerator`. ~2.5 min/5 s, ~5.2 min/10 s on the 4080.
- Local **Llama-3.1 8B** already authors prompts → can absorb the instruction-parse step.

## v1 architecture

**New endpoint:** `POST /api/dream/{id}/interact`
- Body: `{ frame_index | frame_image, x, y, instruction }`
- WS: streams the three latency tiers (below); returns the stitched continuation + branch record.

**Orchestration** (`parse → segment → generate → stitch`):

| Step | Implementation | New? |
|---|---|---|
| Parse instruction → `{target, action}` | existing Llama-3.1 (~100 ms) | reuse |
| Segment `frame + (x,y) + target` → binary mask | hosted **SAM 3** client → `Backend/Python/core/segmentation.py` (provider + API key via env) | **new** |
| Build payload | `frame_N` = I2V first frame; `mask` = region noise-mask; `action` = motion prompt | — |
| Generate continuation | new ComfyLocalMCP `scene_video_ltx2_inpaint.json` — GGUF base + SAM-3 mask via `LTXVSetVideoLatentNoiseMasks`/`LTXVAddLatentGuide`, `frame_N` via `LTXVImgToVideoConditionOnly` (bypass=False = true I2V) | **new** (no model download) |
| Stitch | ffmpeg concat, `frame_N` as the seam (last frame of clip A / first of clip B) | **new** |

**Latency tiers (Apple "decouple acknowledgment from resolution"):**
- **Instant** (<100 ms): tap registered → shimmer/glow on tap point.
- **Fast** (200–800 ms): SAM 3 mask + parsed instruction → object outlined, "thinking" affordance.
- **Slow** (sec+): generation → diegetic pacing beat (darkness/sound/push-in). The dark-dreamlike north-star aesthetic is forgiving here.

**`.imn` schema addition** — a dream becomes a clip tree:
```
interactions: [
  { id, parent_clip, frame_ref, tap: [x,y], instruction,
    target, action, mask_ref, clip_url, generated_at }
]
```

## E2E test (`Backend/Python/test_interactive_pipeline.py`)

1. Generate (or load) a scene → get `frame_N`.
2. Simulate `tap (x,y)` + `instruction` (e.g. "open the door").
3. Assert: mask covers the tapped region; continuation clip renders; stitched mp4 is valid (ffprobe); the **masked region visibly changes** vs. the rest of the frame staying coherent.

## De-risk spikes (do first, before the full wire-up)

1. **SAM 3 hosted** — pick a provider (Replicate / fal / Meta; SAM 3 released 2025-11-19 so confirm availability + get a key), segment a test frame with point + concept prompt → mask. Validate multi-instance disambiguation (hallway-with-multiple-doors style).
2. **Mask-conditioned I2V locally** — feed a mask + `frame_N` + action through `LTXVSetVideoLatentNoiseMasks` on the GGUF stack and confirm the masked region animates per instruction while the rest stays coherent. **This is the linchpin behavior.**

## Open questions

- **SAM 3 provider** + auth (hosted availability for a Nov-2025 model is the main unknown).
- **Action-verb-conditioned mask adjustment** ("open" = panel; "burn" = panel+frame). Panel-only likely fine for v1.
- **Frame extraction** at the pause timestamp (ffmpeg seek on the dream's mp4).
- **Architecture:** standalone interaction function/service vs. a second small LangGraph. Lean standalone for v1.
- Continuous vs on-tap segmentation, pre-labeling interactables — deferred (PDF "Open Architectural Questions").

## Stack summary

| Layer | Choice |
|---|---|
| Instruction parsing | local Llama-3.1 8B |
| Segmentation | hosted SAM 3 (point + concept prompt) |
| Video generation | LTX-2.3 GGUF I2V + region noise-mask (`scene_video_ltx2_inpaint`) |
| Stitch | ffmpeg (`frame_N` seam) |
| Orchestration | `POST /api/dream/{id}/interact` → parse → segment → generate → stitch |
