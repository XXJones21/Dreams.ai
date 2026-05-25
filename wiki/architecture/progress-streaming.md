---
title: Progress Streaming
status: canonical
last_reviewed: 2026-05-23
related:
  - architecture/pipeline.md
  - architecture/visual-generation.md
sources:
  - Backend/Python/core/progress_broker.py
  - Backend/Python/api_server.py
  - src/hooks/useDreamProgress.ts
---

# Progress Streaming

Image and video generation are slow, so the pipeline streams live progress to the frontend over a per-dream WebSocket. This replaced REST polling.

## Path

```
Cenedril{Image,Video}Generator          api_server WS handler          React
  publish_progress(dream_id, event) -->  subscribe(dream_id): Queue --> useDreamProgress
  (LangGraph worker thread)               (asyncio event loop)           (ws.onmessage)
        |                                       ^
        +--------- core/progress_broker --------+
```

## Broker (`core/progress_broker.py`)

A tiny thread-safe in-process pubsub. The whole point is to bridge the **LangGraph worker thread** (where agents run, dispatched via `asyncio.to_thread`) and the **asyncio event loop** (where the WS handler lives).

- `publish(dream_id, event)` — fan out to every subscriber's `queue.Queue` (non-blocking; drops on `queue.Full`).
- `subscribe(dream_id) -> Queue` — register a bounded (256) queue.
- `unsubscribe(dream_id, q)` — remove it; drops the dream key when empty.

In-process only; nothing survives a restart. There is one broker per server process.

## WS handler (`api_server.py:97`)

`@app.websocket("/api/dream/{dream_id}/progress")`:

1. `accept()`, then `subscribe(dream_id)`.
2. Loop draining the queue via `asyncio.to_thread(q.get, True, 30.0)` (so the blocking `get` doesn't stall the loop).
3. On a 35 s timeout, send `{"stage": "heartbeat"}` and continue.
4. Forward each event as JSON.
5. **Close logic:** breaks on a `completed`/`error` event with `kind: "video"`. On an image `completed`/`error`, it keeps the socket open a short grace period for the optional video stage, then closes.
6. `finally: unsubscribe`.

## Event shape

Published by the visual agents (`agents.py`, `publish_progress`):

```json
{"stage": "submit"|"progress"|"executing"|"executed"|"completed"|"error"|"skipped"|"heartbeat",
 "kind": "image"|"video", "workflow": "...", "asset_url": "...", "filepath": "...",
 "prompt_id": "...", "message": "...", "reason": "..."}
```

## Frontend hook (`src/hooks/useDreamProgress.ts`)

`useDreamProgress(dreamId, baseUrl="ws://localhost:8000")` opens the WS and returns `{connected, events[], latest, imageAsset, videoAsset, error}`. It filters out heartbeats and latches `imageAsset`/`videoAsset` from `completed` events so the page can swap in final media without re-fetching the `.imn`. Consumed by `src/pages/DreamDetailPage.tsx`.

## Note

Only the **visual** agents publish progress. The narrative agents (Carthir/Narnion/Review/Cenedril, ~11 s total) emit nothing over the WS — the UI sees no events until the image stage's `submit`. If narrative-phase feedback is wanted, those agents would need `publish_progress` calls too.
