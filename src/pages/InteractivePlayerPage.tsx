import React, { useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { Play, Hand } from "lucide-react";
import { useDreamProgress } from "../hooks/useDreamProgress";

/**
 * MILESTONE 2 PLACEHOLDER — open, unauthenticated `/play/:id` route.
 *
 * This is the future tap-to-segment InteractivePlayer surface (SAM 3 +
 * staggered feedback). For Milestone 1 it ONLY plays the portrait video; there
 * is intentionally NO tap-capture, segmentation, or instruction-parse logic
 * here yet (out of scope). See docs/frontend-redesign-plan.md.
 */
const InteractivePlayerPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const progress = useDreamProgress(id);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  return (
    <div className="flex min-h-[100dvh] flex-col items-center justify-center bg-oled-bg text-oled-text">
      <div className="relative h-[100dvh] w-full max-w-md bg-black">
        {progress.videoAsset ? (
          <>
            <video
              ref={videoRef}
              src={progress.videoAsset}
              className="h-full w-full object-contain"
              playsInline
              controls={isPlaying}
              preload="metadata"
              poster={progress.imageAsset ?? undefined}
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
            />
            {!isPlaying && (
              <button
                onClick={() => videoRef.current?.play()}
                aria-label="Play"
                className="absolute inset-0 flex items-center justify-center bg-black/30 [touch-action:manipulation]"
              >
                <span className="flex h-16 w-16 items-center justify-center rounded-full bg-oled-cta shadow-[0_0_30px_rgba(225,29,72,0.5)]">
                  <Play className="h-7 w-7 translate-x-0.5 text-white" fill="white" />
                </span>
              </button>
            )}
          </>
        ) : (
          <div className="flex h-full flex-col items-center justify-center gap-3 px-6 text-center text-oled-text/50">
            <Hand className="h-8 w-8" />
            <p className="text-sm">
              Interactive player coming in Milestone 2. No video available yet
              for this dream.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default InteractivePlayerPage;
