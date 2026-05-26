# Session Handoff — 2026-05-25

> Resume doc for Dreams.ai. Read `CLAUDE.md` first for durable project context; this is "what just happened / do this next."

## Headline
**The full linear E2E runs on a phone, and the video stage is now true image-to-video.** Prompt → narrative → first-person Flux image → LTX-2.3 GGUF I2V video (start frame = that image) → plays portrait 9:16 on the phone over the tunnel. Image↔video drift is much reduced (motion-only video prompt + gentle camera motion + I2V strength 0.9). The tap-to-pause interactive player shell (E2E #2 Step 2 frontend) is built against a stubbed `/continue`.

## Status
- **Worktrees / branches:**
  - `D:\Dreams.ai` → `main` (durable docs; feature branches **not yet merged**).
  - `D:\Dreams.ai-backend` → `feat/e2e-linear-pipeline` @ `8eaa1f3` (I2V graft + anti-drift agent fixes).
  - `D:\Dreams.ai-frontend` → `feat/mobile-redesign` @ `06aebee` (mobile UI + interactive player).
  - `D:\Tools\ComfyLocalMCP` → `main` (workflow lives here; frame bump uncommitted — see below).
- **GPU stack:** ✅ image (Flux Q4 GGUF) and ✅ video (LTX-2.3 GGUF **I2V**) verified end-to-end through the real Dreams pipeline, on the phone.
- **ComfyUI:** shared with Valinor on `:8188`; ~14.8 GB free at rest. One job at a time; restarts are the user's call.

## What's Done (this session)
- **T2V → I2V (Step 1).** `scene_video_ltx2.json` grafted an image-conditioning branch (`VHS_LoadImagePath` → `LTXVPreprocess` → `LTXVImgToVideoConditionOnly`, nodes 60–63) onto the proven unsloth GGUF graph; the generated Flux frame is now the video start frame. Overrides added: `image_input`, `i2v_strength`, `i2v_bypass`. Strength tuned 0.7 → **0.9**. (`comfy_local_mcp` `281cae1`, `d7555cb`.)
- **Anti-drift agent fixes** (`core/agents.py`, backend `e54cee7`, `a344e06`, `8eaa1f3`):
  - `CenedrilVideoGenerator` now feeds the **local frame path** (`image_block["filepath"]`, not `asset_url`, which `VHS_LoadImagePath` can't read).
  - Video prompt = **POV preamble + motion-only** `cenedril_camera_motion` (no longer re-describes the scene the frame already shows).
  - Cenedril **image** prompt: first-person POV enforced (camera = eyes; forbid figures/bodies/silhouettes/from-behind), LLM preamble + stray quotes stripped.
  - `cenedril_camera_motion` = a **second LLM call** for *gentle, observe-only* motion (forbids lurch/shake/spin/warp/morph/glitch/blur — the big drift driver).
  - Cenedril strict perspective/word-count checks **softened from hard crash → warning** (a flaky validation no longer blocks the image stage).
- **Mobile-first frontend** (frontend worktree): OLED theme + primitives, env-driven `API_BASE_URL`, Vite `/api` + `/comfy` proxies, `mediaUrl` rewrite (`127.0.0.1:8188` → same-origin so the phone loads assets), async create + **progressive display** (poll `.imn`, seed media, WS heartbeat), refreshed `/create` example prompts.
- **Interactive player (Step 2 frontend, `b5e9f15`):** `InteractivePlayerPage` — fullscreen-on-play, tap-to-pause, `<canvas>` frame capture + normalized tap (x,y), scene `actions` as chips → POST to a **stubbed** `/continue`.
- **Robustness:** async `POST /api/dream` (background thread + single-flight 409) to dodge the Cloudflare 524 tunnel timeout; WS handler catches `queue.Empty` → heartbeat; `imn_to_dreamcard` reads title/story from `pre_production` + exposes media URLs.
- **Duration bump (uncommitted, this turn):** `scene_video_ltx2.json` node 10 `frames` 121 → **241** (~10 s) per the user's call; description carries a revert note. **Untested with I2V on 16 GB — the ×2 upscale peak may OOM; drop back to 121 if it does.**
- **Docs:** `interactive-video-segmentation-pipeline.pdf` + `docs/interactive-video-pipeline-design.md` + `docs/frontend-redesign-plan.md` added; this `CLAUDE.md` + `SESSION_HANDOFF.md` updated.

## What's Pending (next, in priority order)
1. **Confirm the 10 s (241-frame) run** completes without OOM on the phone test, and judge full-clip drift. If it OOMs → revert node 10 to 121 and commit at 5 s.
2. **Step 2 backend (`#30`):** `POST /api/dream/{id}/continue` (multipart paused-frame PNG + action + tap x/y → I2V stage with paused frame as `image_input`, action as the motion prompt → append a scene, stream over WS, single-flight guarded) + add `scene_context`/`actions` to the `imn_to_dreamcard` GET projection. Integrate the stubbed frontend `continueDream` against it.
3. **Merge to `main`:** fold `feat/e2e-linear-pipeline` + `feat/mobile-redesign` (and commit the ComfyLocalMCP frame bump) back to `main` to re-sync, as last round.
4. **Agent-parse robustness:** retry/tolerance for transient Narnion/director parse failures so one flaky LLM call doesn't crash the whole dream.
5. **LTX-Director spike** (interaction/continuity milestone): install the `LTXDirector` node + checkpoint, graft into the GGUF graph for stronger directed motion / scene continuity — the real lever for residual drift the (OOMing) stage-2 conditioning can't provide here.
6. Earlier deferred image levers: t5 fp8 swap, Flux Krea, first-class `state["aspect_ratio"]`.

## Gotchas for Next Session
- **I2V needs the frame PATH, not the URL** — `VHS_LoadImagePath` reads from disk; `asset_url` (`http://127.0.0.1:8188/...`) won't load.
- **The video prompt must drive MOTION, not re-describe the scene** — the start frame sets the scene; re-describing it fights the conditioning and causes drift. Keep motion gentle (no lurch/shake/blur).
- **Stage-2 latent conditioning OOMs the 16 GB card** at the ×2 upscale peak — don't re-add it; that's why residual end-drift remains and why LTX-Director is the path.
- **241 frames (10 s) + I2V + ×2 upscale is near the VRAM ceiling** — watch for OOM; node 10 `frames` reverts to 121 for 5 s.
- **The connector is still the whole ballgame for LTX-2.3 GGUF text:** `DualCLIPLoaderGGUF` clip2 = `…embeddings_connectors.safetensors`, NOT text_projection. Plus the kornia `pad = F.pad` shim (overwritten on node-pack update). See `CLAUDE.md`.
- **Shared ComfyUI/GPU with Valinor** — one heavy job at a time; don't restart/free without asking. Don't run authenticated tunnels.

## Reference Material
- **Working LTX-2.3 recipe + gotchas:** memory `ltx23-gguf-video-works`; `scene_video_ltx2.json` `_meta.notes`; Engram `Projects/dreams-ai/claude.md`.
- **Interactive design doc:** `docs/interactive-video-segmentation-pipeline.pdf` + `docs/interactive-video-pipeline-design.md`.
- **Aesthetic North Star:** The Archive In Between, Gloomstomper/@voidstomper (portrait 9:16 first-person dark/dreamlike shorts).
