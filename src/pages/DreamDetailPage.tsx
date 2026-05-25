import React, { useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, AlertCircle, Play, Loader2 } from "lucide-react";
import MobileNav from "../components/ui/MobileNav";
import Button from "../components/ui/Button";
import { useDreamProgress, type DreamProgressEvent } from "../hooks/useDreamProgress";
import { fetchDream, ApiError, API_BASE_URL, mediaUrl } from "../lib/api";
import type { Dream } from "../components/feed/DreamCard";

const STAGE_LABELS: Record<string, string> = {
  submit: "Queued",
  progress: "Generating",
  executing: "Generating",
  executed: "Rendering",
  completed: "Done",
  skipped: "Skipped",
  error: "Error",
};

function describe(ev: DreamProgressEvent | null): string {
  if (!ev) return "Connecting…";
  const kind = ev.kind === "video" ? "Video" : ev.kind === "image" ? "Image" : "Scene";
  const stage = STAGE_LABELS[ev.stage] ?? ev.stage;
  const pct = typeof ev.percent === "number" ? ` · ${ev.percent}%` : "";
  return `${kind} · ${stage}${pct}`;
}

const DreamDetailPage: React.FC = () => {
  const { dreamId } = useParams<{ dreamId: string }>();
  const navigate = useNavigate();
  const [dream, setDream] = useState<Dream | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const progress = useDreamProgress(dreamId);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    if (!dreamId) return;
    const ac = new AbortController();
    let stop = false;
    let timer: ReturnType<typeof setTimeout>;
    setLoading(true);
    setError(null);
    const poll = async () => {
      try {
        const data = (await fetchDream(dreamId, ac.signal)) as Dream;
        if (stop) return;
        setDream(data);
        setLoading(false);
        setError(null);
        // The .imn is the source of truth for assets — keep polling until the
        // video lands so a missed WS event still surfaces the finished media.
        if (!data?.video_url) timer = setTimeout(poll, 2500);
      } catch (err) {
        if (stop || ac.signal.aborted) return;
        if (err instanceof ApiError && err.status === 404) {
          // Async pipeline just started; the .imn isn't written yet — keep waiting.
          timer = setTimeout(poll, 2000);
          return;
        }
        setError(err instanceof ApiError ? err.message : "Failed to load dream");
        setLoading(false);
      }
    };
    poll();
    return () => {
      stop = true;
      ac.abort();
      clearTimeout(timer);
    };
  }, [dreamId]);

  // Live WS asset wins; otherwise fall back to whatever the .imn already has.
  // Rewrite ComfyUI localhost:8188 URLs to the same-origin /comfy proxy so they
  // load on a phone over the tunnel.
  const imageSrc = mediaUrl(progress.imageAsset ?? dream?.image_url ?? null);
  const videoSrc = mediaUrl(progress.videoAsset ?? dream?.video_url ?? null);

  const videoBusy =
    progress.latest?.kind === "video" &&
    !["completed", "error", "skipped"].includes(progress.latest.stage);
  const showProgress =
    !videoSrc && (progress.latest != null || progress.connected);

  return (
    <div className="min-h-[100dvh] bg-oled-bg text-oled-text">
      <MobileNav
        left={
          <button
            onClick={() => navigate(-1)}
            aria-label="Back"
            className="inline-flex min-h-touch min-w-touch cursor-pointer items-center justify-center rounded-lg text-oled-text/70 [touch-action:manipulation] hover:text-oled-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-oled-cta"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
        }
      />

      <main className="mx-auto flex max-w-2xl flex-col gap-5 px-4 pb-[max(2rem,env(safe-area-inset-bottom))] pt-6">
        {loading && <SkeletonState />}

        {!loading && error && (
          <ErrorState message={error} onRetry={() => window.location.reload()} />
        )}

        {!loading && !error && dream && (
          <>
            <header>
              <h1 className="text-2xl font-bold leading-tight">
                {dream.title || "Untitled dream"}
              </h1>
              {dream.excerpt && (
                <p className="mt-2 text-sm text-oled-text/60">{dream.excerpt}</p>
              )}
            </header>

            {/* Portrait media stage */}
            <div className="relative mx-auto w-full max-w-sm overflow-hidden rounded-2xl border border-white/10 bg-black">
              <div className="relative aspect-[9/16] w-full">
                {videoSrc ? (
                  <>
                    <video
                      ref={videoRef}
                      src={videoSrc}
                      className="absolute inset-0 h-full w-full object-contain"
                      playsInline
                      controls={isPlaying}
                      preload="metadata"
                      poster={imageSrc ?? undefined}
                      onPlay={() => setIsPlaying(true)}
                      onPause={() => setIsPlaying(false)}
                    />
                    {!isPlaying && (
                      <button
                        onClick={() => videoRef.current?.play()}
                        aria-label="Play video"
                        className="absolute inset-0 flex items-center justify-center bg-black/30 [touch-action:manipulation]"
                      >
                        <span className="flex h-16 w-16 items-center justify-center rounded-full bg-oled-cta shadow-[0_0_30px_rgba(225,29,72,0.5)]">
                          <Play className="h-7 w-7 translate-x-0.5 text-white" fill="white" />
                        </span>
                      </button>
                    )}
                  </>
                ) : imageSrc ? (
                  <img
                    src={imageSrc}
                    alt="Generated scene"
                    className="absolute inset-0 h-full w-full object-contain"
                  />
                ) : (
                  <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 text-oled-text/50">
                    <Loader2 className="h-7 w-7 animate-spin motion-reduce:animate-none" />
                    <p className="text-sm">Dreaming up the first frame…</p>
                  </div>
                )}
              </div>
            </div>

            {/* Progress / status line */}
            {showProgress && (
              <div
                role="status"
                aria-live="polite"
                className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-oled-primary px-4 py-3 text-sm"
              >
                {(videoBusy || !progress.latest) && (
                  <Loader2 className="h-4 w-4 animate-spin text-oled-cta motion-reduce:animate-none" />
                )}
                <span className="text-oled-text/80">{describe(progress.latest)}</span>
                {!progress.connected && (
                  <span className="text-oled-text/40">(stream offline)</span>
                )}
              </div>
            )}

            {progress.error && (
              <p className="text-center text-sm text-oled-cta">{progress.error}</p>
            )}

            <Button variant="secondary" fullWidth onClick={() => navigate("/create")}>
              Dream again
            </Button>
          </>
        )}

        <p className="mt-2 text-center text-xs text-oled-text/30">
          Backend: {API_BASE_URL}
        </p>
      </main>
    </div>
  );
};

const SkeletonState: React.FC = () => (
  <div className="flex flex-col gap-5" aria-hidden="true">
    <div className="h-7 w-2/3 animate-pulse rounded bg-white/10 motion-reduce:animate-none" />
    <div className="mx-auto aspect-[9/16] w-full max-w-sm animate-pulse rounded-2xl bg-white/5 motion-reduce:animate-none" />
  </div>
);

const ErrorState: React.FC<{ message: string; onRetry: () => void }> = ({
  message,
  onRetry,
}) => (
  <div className="flex flex-col items-center gap-4 rounded-2xl border border-white/10 bg-oled-primary px-5 py-10 text-center">
    <AlertCircle className="h-10 w-10 text-oled-cta" />
    <div>
      <p className="font-bold">Couldn’t load this dream</p>
      <p className="mt-1 text-sm text-oled-text/60">{message}</p>
    </div>
    <Button variant="secondary" onClick={onRetry}>
      Try again
    </Button>
  </div>
);

export default DreamDetailPage;
