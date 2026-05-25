import React, { useEffect } from "react";
import { X } from "lucide-react";

interface SheetProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
}

/**
 * Bottom sheet for mobile. Slides up from the bottom edge, dims the backdrop,
 * respects safe-area insets and prefers-reduced-motion. z-30 per the player
 * z-index scale (above mask/shimmer, below toast).
 */
const Sheet: React.FC<SheetProps> = ({ open, onClose, title, children }) => {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  return (
    <div
      className={
        "fixed inset-0 z-30 transition-opacity duration-200 " +
        (open ? "pointer-events-auto opacity-100" : "pointer-events-none opacity-0")
      }
      aria-hidden={!open}
    >
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className={
          "absolute inset-x-0 bottom-0 rounded-t-2xl border-t border-white/10 bg-oled-primary " +
          "px-5 pb-[max(1.25rem,env(safe-area-inset-bottom))] pt-4 " +
          "transition-transform duration-300 motion-reduce:transition-none " +
          (open ? "translate-y-0" : "translate-y-full")
        }
      >
        <div className="mx-auto mb-3 h-1 w-10 rounded-full bg-white/20" />
        <div className="mb-3 flex items-center justify-between">
          {title && (
            <h2 className="text-base font-bold text-oled-text">{title}</h2>
          )}
          <button
            onClick={onClose}
            aria-label="Close"
            className="ml-auto inline-flex min-h-touch min-w-touch cursor-pointer items-center justify-center rounded-lg text-oled-text/70 [touch-action:manipulation] hover:text-oled-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-oled-cta"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
};

export default Sheet;
