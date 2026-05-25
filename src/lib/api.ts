// Centralized, env-driven API configuration.
//
// VITE_API_BASE_URL controls where the frontend talks to the Dreams.ai backend
// (FastAPI on :8000 by default). The WebSocket base is derived from it so the
// phone/tunnel only needs ONE origin configured.
//
// Examples:
//   VITE_API_BASE_URL=http://localhost:8000        -> ws://localhost:8000
//   VITE_API_BASE_URL=https://dreams.example.com   -> wss://dreams.example.com

// Default to SAME-ORIGIN (empty base) so REST/WS go through the Vite dev proxy
// (see vite.config.ts) — one tunnel, no CORS. Set VITE_API_BASE_URL to talk to a
// separate backend origin directly instead (e.g. http://localhost:8000).
export const API_BASE_URL: string = (
  (import.meta.env.VITE_API_BASE_URL as string | undefined) || ""
).replace(/\/+$/, "");

/** WS/WSS base. Derived from the API base, or from the page origin when same-origin. */
export const WS_BASE_URL: string = API_BASE_URL
  ? API_BASE_URL.replace(/^http/, "ws")
  : typeof window !== "undefined"
    ? `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}`
    : "";

/** Build a full REST URL for a backend path (path may start with or without `/`). */
export function apiUrl(path: string): string {
  return `${API_BASE_URL}/${path.replace(/^\/+/, "")}`;
}

/** Build a full WS URL for a backend path. */
export function wsUrl(path: string): string {
  return `${WS_BASE_URL}/${path.replace(/^\/+/, "")}`;
}

/**
 * Rewrite a ComfyUI asset URL (`http://127.0.0.1:8188/view?...`) to a
 * same-origin `/comfy/...` path so it loads through the Vite dev proxy — the
 * raw localhost:8188 host is unreachable from a phone over the tunnel.
 * Pass-through for null or non-ComfyUI URLs.
 */
export function mediaUrl(raw: string | null | undefined): string | null {
  if (!raw) return null;
  return raw.replace(/^https?:\/\/(127\.0\.0\.1|localhost):8188/i, "/comfy");
}

export type CreateDreamResponse = {
  id: string;
  dream_name?: string | null;
  story_prompt?: string | null;
  initial_goal?: string | null;
  pitch?: string | null;
  imn_filename?: string;
};

export class ApiError extends Error {
  status?: number;
  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

/**
 * POST /api/dream — submit a text prompt to start the narrative+visual pipeline.
 *
 * NOTE: the backend currently runs the pipeline SYNCHRONOUSLY and only returns
 * once narration (and, with generate_video, the visual stages) complete. This
 * can take several minutes. Callers should show an indeterminate "dreaming"
 * state and not assume a fast response. The returned `id` is the dream UUID.
 */
export async function createDream(
  prompt: string,
  signal?: AbortSignal
): Promise<CreateDreamResponse> {
  let res: Response;
  try {
    res = await fetch(apiUrl("/api/dream"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
      signal,
    });
  } catch (err) {
    throw new ApiError(
      "Could not reach the Dreams.ai backend. Is it running on " + API_BASE_URL + "?"
    );
  }
  if (!res.ok) {
    throw new ApiError(`Dream creation failed (${res.status})`, res.status);
  }
  return (await res.json()) as CreateDreamResponse;
}

/** GET /api/dreams/:id — fetch the DreamCard-shaped projection of an .imn. */
export async function fetchDream(dreamId: string, signal?: AbortSignal) {
  let res: Response;
  try {
    res = await fetch(apiUrl(`/api/dreams/${dreamId}`), { signal });
  } catch (err) {
    throw new ApiError("Could not reach the Dreams.ai backend at " + API_BASE_URL);
  }
  if (res.status === 404) throw new ApiError("Dream not found", 404);
  if (!res.ok) throw new ApiError(`Failed to load dream (${res.status})`, res.status);
  return res.json();
}
