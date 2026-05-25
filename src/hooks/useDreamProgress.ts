import { useEffect, useRef, useState } from "react";

export type DreamProgressEvent = {
  stage: "submit" | "progress" | "executing" | "executed" | "completed" | "error" | "skipped" | "heartbeat";
  kind?: "image" | "video";
  workflow?: string;
  percent?: number;
  value?: number;
  max?: number;
  message?: string;
  reason?: string;
  asset_url?: string | null;
  filepath?: string | null;
  prompt_id?: string | null;
};

export type DreamProgressState = {
  connected: boolean;
  events: DreamProgressEvent[];
  latest: DreamProgressEvent | null;
  imageAsset: string | null;
  videoAsset: string | null;
  error: string | null;
};

/**
 * Subscribes to the backend's per-dream WS progress stream.
 *
 * Heartbeats are filtered out before reaching React state. The hook
 * tracks the most recently completed image/video asset URL so the page
 * can swap in the final media without re-fetching the IMN.
 */
export function useDreamProgress(dreamId: string | undefined, baseUrl: string = "ws://localhost:8000"): DreamProgressState {
  const [state, setState] = useState<DreamProgressState>({
    connected: false,
    events: [],
    latest: null,
    imageAsset: null,
    videoAsset: null,
    error: null,
  });
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!dreamId) return;
    const ws = new WebSocket(`${baseUrl}/api/dream/${dreamId}/progress`);
    wsRef.current = ws;

    ws.onopen = () => setState((prev) => ({ ...prev, connected: true, error: null }));
    ws.onerror = () =>
      setState((prev) => ({ ...prev, error: "progress stream error" }));
    ws.onclose = () => setState((prev) => ({ ...prev, connected: false }));
    ws.onmessage = (msg) => {
      try {
        const event = JSON.parse(msg.data) as DreamProgressEvent;
        if (event.stage === "heartbeat") return;
        setState((prev) => ({
          ...prev,
          events: [...prev.events, event],
          latest: event,
          imageAsset:
            event.kind === "image" && event.stage === "completed" && event.asset_url
              ? event.asset_url
              : prev.imageAsset,
          videoAsset:
            event.kind === "video" && event.stage === "completed" && event.asset_url
              ? event.asset_url
              : prev.videoAsset,
        }));
      } catch {
        // ignore malformed payload; the backend always sends JSON
      }
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [dreamId, baseUrl]);

  return state;
}
