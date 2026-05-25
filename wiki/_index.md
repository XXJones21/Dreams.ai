---
title: Wiki Index
status: canonical
last_reviewed: 2026-05-23
related: [README.md, _summaries.md, operations/status-and-roadmap.md]
---

# Wiki Index

Entry point for the Dreams.ai wiki. Read this first. Every other article is reachable from here.

Dreams.ai turns a text prompt into an interactive, illustrated "dream": a LangGraph pipeline of narrative agents (local Llama-3.1 8B) followed by visual agents that generate images and video through a local ComfyUI. Current product focus: **portrait 9:16, first-person, dark/dreamlike short-form video**. See repo [`CLAUDE.md`](../CLAUDE.md) → "Aesthetic North Star".

## Start here, by goal

### "I'm new — how does this work end to end?"

1. [architecture/overview.md](architecture/overview.md) — What Dreams.ai is and how the pieces fit.
2. [architecture/pipeline.md](architecture/pipeline.md) — The LangGraph agent graph, step by step.
3. [backend/imn-format.md](backend/imn-format.md) — The `.imn` file that threads state through every agent.

### "I want to generate images/video"

1. [architecture/visual-generation.md](architecture/visual-generation.md) — ComfyUI + `engram_comfy` harness, workflows, models.
2. [architecture/progress-streaming.md](architecture/progress-streaming.md) — How progress reaches the React UI over WebSocket.
3. [operations/testing.md](operations/testing.md) — How to run the stack and fire a test dream.

### "What's the state of the project — what's done, pending, removable?"

1. [operations/status-and-roadmap.md](operations/status-and-roadmap.md) — **The living status doc.** What works, what's broken, what to delete.

### "I'm changing the backend agents"

1. [architecture/pipeline.md](architecture/pipeline.md) — Supervisor routing and agent contracts.
2. [backend/imn-format.md](backend/imn-format.md) — The schema each agent reads/writes.
3. [operations/status-and-roadmap.md](operations/status-and-roadmap.md) — Known issues and legacy code before you touch anything.

## Topic tree

### Architecture
- [architecture/overview.md](architecture/overview.md)
- [architecture/pipeline.md](architecture/pipeline.md)
- [architecture/visual-generation.md](architecture/visual-generation.md)
- [architecture/progress-streaming.md](architecture/progress-streaming.md)

### Backend
- [backend/imn-format.md](backend/imn-format.md)

### Operations
- [operations/testing.md](operations/testing.md)
- [operations/status-and-roadmap.md](operations/status-and-roadmap.md)

## Related docs outside the wiki

- [`CLAUDE.md`](../CLAUDE.md) — Durable project instructions, local inference setup, benchmarks, aesthetic north star.
- [`TESTING.md`](../TESTING.md) — Canonical run guide.
- [`SESSION_HANDOFF.md`](../SESSION_HANDOFF.md) — Latest session handoff.
- Engram: `D:\Tools\Valinor\Engram\Projects\dreams-ai\claude.md` — cross-session brain.

## Status legend

- **canonical** — Reviewed against code, current, safe to cite.
- **draft** — Partially verified. Cite cautiously.
- **stale** — Known out of date.
