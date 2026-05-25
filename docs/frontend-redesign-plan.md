# Frontend Redesign Plan — Mobile-First Interactive Player

> Plan for redesigning the Dreams.ai frontend so the **gesture-driven segmentation E2E test can be dogfooded on a phone** (touch input drives SAM 3). Companion to [`interactive-video-pipeline-design.md`](./interactive-video-pipeline-design.md). Design system generated via the `ui-ux-pro-max` skill → persisted at `design-system/dreams.ai/`. Drafted 2026-05-25.

## Why

SAM 3 segmentation is **touch-based** (tap an object), so the test surface must run on a phone. The current frontend is desktop-minimal and not touch/mobile ready. We dogfood the interactive loop on a real device.

## Current state (review)

- **Stack:** Vite + React 18 + TypeScript + Tailwind 3 + React Router 6 + Supabase + lucide-react. No component library. (Project began as `luxury-cosmic-landing` — decorative cosmic landing: `CosmicBackground`, `MarbleBust`, `ArtDecoColumns`.)
- **Routing** (`src/App.tsx`): `/` cosmic home, `/feed` + `/dreams` (FeedPage), `/dreams/:dreamId` (DreamDetailPage), `/profile`, auth routes.
- **`DreamDetailPage`** (the test surface) is minimal: fetches `http://localhost:8000/api/dreams/:id`, renders a `DreamCard` + progress text + plain `<img>`/`<video controls>` at `max-w-2xl`. **No pause-to-tap, no touch capture, no instruction input, no staggered feedback.**
- **Blockers for phone use:** (1) **hardcoded `http://localhost:8000`** in `DreamDetailPage` and the WS URL in `useDreamProgress` — unreachable from a phone; (2) no mobile-first layout; (3) no `<meta viewport>` audit.

## Design system (from ui-ux-pro-max → `design-system/dreams.ai/`)

- **Style:** Dark Mode (OLED) — deep black, high contrast, WCAG AAA, fits the dark/dreamlike north star.
- **Palette:** bg `#000000`, primary `#0F0F23`, secondary/midnight `#1E1B4B`, **CTA play-red `#E11D48`**, text `#F8FAFC`.
- **Type:** Atkinson Hyperlegible (accessible/legible) for UI; keep a display face for branding if desired.
- **Pattern:** Minimal single column, mobile-first, one primary action — exactly right for a distraction-free player.
- **Effects:** minimal glow (`text-shadow: 0 0 10px`), visible focus, `prefers-reduced-motion` respected. **Anti-patterns to avoid:** static layout, slow video player.

## Scope — FULL mobile redesign (decided)

**Keep:** the stack (Vite/React/TS/Tailwind/Supabase/router), Supabase auth, the overall information architecture.
**Redesign mobile-first with the OLED theme:** every primary surface — **home, feed, nav/header, and the new InteractivePlayer** — rebuilt responsive and touch-first on the shared dark-OLED token set. The decorative cosmic landing components (`MarbleBust`, `ArtDecoColumns`, `CosmicBackground`) are demoted to optional accents (or retired) in favor of the minimal-single-column, performance-first pattern. The **InteractivePlayer is the priority surface** (it gates the E2E dogfood) but ships within a coherent mobile redesign.

### Decisions (locked 2026-05-25)
- **Devices: both iOS + Android → serve over an HTTPS tunnel from the start** (Cloudflare Tunnel / ngrok) so behavior is identical and secure-context APIs (vibrate, etc.) work on iOS too.
- **Auth: open, unauthenticated `/play/:id` test route** for dogfooding (no Supabase login on the phone); lock down before production.
- **Scope: full mobile redesign** (not player-only).

## Centerpiece: `InteractivePlayer`

A portrait 9:16, touch-first player implementing the PDF's staggered-feedback loop.

- **Video:** `playsInline`, click-to-play (no autoplay), portrait container `aspect-[9/16]` capped to viewport height, `object-contain`, black letterbox.
- **Pause → tap to segment:**
  - Capture tap via `onPointerDown` (covers touch + mouse). Compute **normalized** coords `(x,y) ∈ [0,1]` relative to the *rendered video rect*, then map to the video's intrinsic resolution for SAM 3 (`videoWidth/Height`). Account for `object-contain` letterboxing.
  - `touch-action: manipulation` on the surface (removes the 300 ms tap delay — essential for the <100 ms shimmer).
  - **Instant tier (<100 ms):** shimmer/glow ring at the tap point + `navigator.vibrate(10)` haptic. Pure CSS transform/opacity, `prefers-reduced-motion` aware.
- **Instruction input:** bottom sheet with a 16px-min text field (prevents iOS zoom), 44×44px submit, optional speech-to-text (`SpeechRecognition`) later. Clear loading/disabled state on submit.
- **Fast tier (200–800 ms):** render the returned SAM 3 mask as an outlined overlay (SVG/canvas path) on the paused frame + "thinking" affordance on the prompt.
- **Slow tier (sec+):** generation → diegetic pacing beat (dim, subtle audio, slow push-in) while WS streams progress; then the **stitched continuation autoplays**, seamless at `frame_N`.
- **State:** a `useInteraction(dreamId)` custom hook (mirrors `useDreamProgress`) holding `{phase: idle|tapped|masking|generating|playing, tap, mask, clipUrl}`; derive UI from phase (don't over-store).

### z-index scale
video `z-0` · mask overlay `z-10` · tap shimmer `z-20` · instruction sheet `z-30` · progress/toast `z-40`.

## Infrastructure changes (required for phone access)

1. **Env-configurable API base** — add `VITE_API_BASE_URL` (+ derive WS URL). Replace the hardcoded `http://localhost:8000` in `DreamDetailPage` and `useDreamProgress`. Centralize in `src/lib/api.ts`.
2. **HTTPS tunnel (decided, both devices)** — serve Vite + the API through a tunnel (Cloudflare Tunnel or ngrok) so the phone hits an `https://` origin and iOS secure-context APIs (vibrate, speech) work. `server.host = true` + `server.allowedHosts` for the tunnel domain; `VITE_API_BASE_URL` → the tunneled API origin. Document the tunnel setup in TESTING.md. (Plain LAN `http://<dev-IP>` remains a fallback for Android-only quick checks.)
3. **Backend CORS** — currently hardcoded to a Netlify URL (known issue); make env-driven and allow the tunnel origin(s).
4. **`<meta viewport>`** — confirm `width=device-width, initial-scale=1` in `index.html`.
5. **Open test route** — add unauthenticated `/play/:id` (and the interactive player there) outside `ProtectedRoute` for dogfooding.

## Build phases

1. **Plumbing + tunnel:** `src/lib/api.ts` (env base URL + WS), wire `DreamDetailPage`/`useDreamProgress` to it, Vite `host`/`allowedHosts`, env-driven backend CORS, viewport meta, HTTPS tunnel script + TESTING.md notes. → phone can already load + view a dream over https.
2. **Theme system:** Tailwind config extend with the OLED palette + Atkinson Hyperlegible; shared primitives (Button, Sheet, Card, NavBar) at 44px targets, `touch-action: manipulation`, reduced-motion-aware.
3. **`InteractivePlayer`** at open `/play/:id`: portrait player + pause + `onPointerDown` tap-capture + shimmer + `vibrate(10)` + instruction sheet, wired to `POST /interact` (stub until the backend spike lands). The priority surface.
4. **Staggered feedback:** mask overlay (fast tier) + generation pacing (slow tier) + stitched-clip playback, driven by the WS tiers.
5. **Full mobile redesign of the rest:** home, feed (+ `DreamCard`/filters/infinite-scroll), header/nav rebuilt mobile-first on the OLED theme; demote/retire the cosmic decorative components.
6. **Polish pass:** responsive 375/768/1024/1440, a11y + pre-delivery checklist, reduced-motion, performance (no autoplay, lazy media).

## Pre-delivery checklist (from skill)

- [ ] 44×44px touch targets, ≥8px spacing, `touch-action: manipulation`
- [ ] No emoji icons (lucide-react SVG), `cursor-pointer` on clickables
- [ ] Body text ≥16px on mobile, no horizontal scroll, responsive at 375/768/1024/1440
- [ ] Visible focus states, color not the only indicator, alt text + input labels
- [ ] `prefers-reduced-motion` respected; transitions 150–300ms via transform/opacity
- [ ] No autoplay; `playsInline muted preload="none"` until play

## Open questions (remaining)

- **Tunnel choice:** Cloudflare Tunnel (free, named, no time limit) vs ngrok (simpler, ephemeral URLs). Cloudflare preferred for a stable origin in CORS.
- **Coordinate fidelity:** confirm the normalized→intrinsic mapping with `object-contain` letterboxing on a real portrait clip (a small spike).
- **Theme migration depth:** how much of the cosmic identity to preserve as accents vs. fully retire for the minimal OLED look.

*Resolved 2026-05-25:* devices = both (→ HTTPS tunnel); auth = open `/play/:id` test route; scope = full mobile redesign.
