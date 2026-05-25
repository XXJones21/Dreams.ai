import React, { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Sparkles, Loader2 } from "lucide-react";
import MobileNav from "../components/ui/MobileNav";
import Button from "../components/ui/Button";
import TextField from "../components/ui/TextField";
import { createDream, ApiError, API_BASE_URL } from "../lib/api";

const EXAMPLES = [
  "A first-person walk through a flooded cathedral at midnight",
  "Drifting down an endless neon corridor that keeps folding back on itself",
  "Waking inside a house where every door opens onto the same dark forest",
];

const CreateDreamPage: React.FC = () => {
  const navigate = useNavigate();
  const [prompt, setPrompt] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const canSubmit = prompt.trim().length >= 4 && !submitting;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;
    setError(null);
    setSubmitting(true);
    abortRef.current = new AbortController();
    try {
      const res = await createDream(prompt.trim(), abortRef.current.signal);
      if (!res?.id) throw new ApiError("Backend returned no dream id.");
      navigate(`/dreams/${res.id}`);
    } catch (err) {
      const msg =
        err instanceof ApiError
          ? err.message
          : "Something went wrong starting your dream.";
      setError(msg);
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-[100dvh] bg-oled-bg text-oled-text">
      <MobileNav />
      <main className="mx-auto flex max-w-2xl flex-col gap-6 px-4 pb-[max(2rem,env(safe-area-inset-bottom))] pt-8">
        <div>
          <h1 className="text-3xl font-bold leading-tight [text-shadow:0_0_18px_rgba(225,29,72,0.25)]">
            Dream something
          </h1>
          <p className="mt-2 text-base text-oled-text/60">
            Describe a scene. A portrait, first-person short film is generated on
            your machine — narrative, image, then video.
          </p>
        </div>

        {submitting ? (
          <DreamingState prompt={prompt.trim()} />
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <TextField
              label="Your dream prompt"
              hideLabel
              placeholder="A first-person walk through a flooded cathedral at midnight…"
              rows={5}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              error={error}
              autoFocus
            />

            <div className="flex flex-wrap gap-2" aria-label="Example prompts">
              {EXAMPLES.map((ex) => (
                <button
                  key={ex}
                  type="button"
                  onClick={() => setPrompt(ex)}
                  className="cursor-pointer rounded-full border border-white/10 bg-oled-primary px-3 py-2 text-left text-xs text-oled-text/70 [touch-action:manipulation] transition-colors hover:border-white/25 hover:text-oled-text"
                >
                  {ex}
                </button>
              ))}
            </div>

            <Button type="submit" disabled={!canSubmit} fullWidth>
              <Sparkles className="h-5 w-5" />
              Generate dream
            </Button>
          </form>
        )}

        <p className="mt-2 text-center text-xs text-oled-text/30">
          Backend: {API_BASE_URL}
        </p>
      </main>
    </div>
  );
};

/**
 * Shown while POST /api/dream is in flight. The backend runs the pipeline
 * synchronously (minutes), so this is an honest indeterminate state — we cannot
 * subscribe to per-stage WS progress until the dream id comes back. Once it
 * does, we navigate to the dream page which connects the progress stream.
 */
const DreamingState: React.FC<{ prompt: string }> = ({ prompt }) => (
  <div
    role="status"
    aria-live="polite"
    className="flex flex-col items-center gap-4 rounded-2xl border border-white/10 bg-oled-primary px-5 py-10 text-center"
  >
    <Loader2 className="h-8 w-8 animate-spin text-oled-cta motion-reduce:animate-none" />
    <div>
      <p className="font-bold">Dreaming…</p>
      <p className="mt-1 text-sm text-oled-text/60">
        Generating narrative and video on-device. This can take a few minutes —
        keep this screen open.
      </p>
    </div>
    {prompt && (
      <p className="max-w-md text-sm italic text-oled-text/40">“{prompt}”</p>
    )}
  </div>
);

export default CreateDreamPage;
