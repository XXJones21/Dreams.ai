# Dreams.ai Wiki

An LLM-curated knowledge base for the Dreams.ai interactive storytelling platform. A small set of canonical concept articles that humans and language models can both consume cheaply — modeled on the Valinor wiki.

## What lives here

| Path | Purpose |
| --- | --- |
| [`_index.md`](_index.md) | Always-consulted entry point. Topic map and start-here-by-role. |
| [`_summaries.md`](_summaries.md) | One-paragraph blurb per article for fast lookup. |
| `architecture/` | System-wide concepts: pipeline, visual generation, progress streaming. |
| `backend/` | Backend-specific detail: the `.imn` file format, agents. |
| `operations/` | Testing, status, roadmap, and what-can-be-removed. |
| `raw/` | Ingest staging for source docs awaiting compilation. Never linked from articles. |

## How to use

1. **Start at [`_index.md`](_index.md).** It tells you which articles to read for your goal.
2. **Follow links.** Every article cross-references its neighbors with relative paths.
3. **Look up concepts in [`_summaries.md`](_summaries.md)** when you need a one-paragraph reminder.

This wiki is authoritative for *concepts and current state*. The repo root [`CLAUDE.md`](../CLAUDE.md) remains the durable project-instruction file; [`TESTING.md`](../TESTING.md) is the canonical run guide; the cross-session brain is Engram (`Projects/dreams-ai/claude.md`). When they disagree, the wiki is authoritative for architecture and the live status doc ([`operations/status-and-roadmap.md`](operations/status-and-roadmap.md)) for what's done/pending.

## Article frontmatter

```markdown
---
title: Pipeline
status: canonical
last_reviewed: 2026-05-23
related: [architecture/overview.md, backend/imn-format.md]
sources: [Backend/Python/core/agents.py]
---
```

| Field | Required | Meaning |
| --- | --- | --- |
| `title` | yes | Display name. Matches the H1. |
| `status` | yes | `canonical`, `draft`, or `stale`. |
| `last_reviewed` | yes | ISO date of last review. |
| `related` | no | Sibling articles, relative paths from `wiki/`. |
| `sources` | no | Code files or docs the article was distilled from. |

### Status legend

- **canonical** — Reviewed against the code, current, safe to cite.
- **draft** — In progress or partially verified. Cite cautiously.
- **stale** — Known out of date. Pending revision.

## Conventions

- Markdown only. Relative links only.
- One H1 per article, matching `title`.
- Code fences use language tags. Diagrams use Mermaid or ASCII.
- Keep articles short (aim < 300 lines). Split if they grow.
- Cite code as `path:line` so links are clickable.
