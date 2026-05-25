import React from "react";
import { Link } from "react-router-dom";
import { Moon } from "lucide-react";

interface MobileNavProps {
  /** Optional left slot (e.g. a back button). */
  left?: React.ReactNode;
  /** Optional right slot. */
  right?: React.ReactNode;
}

/**
 * Compact, mobile-first top bar on the OLED theme. Sticky, safe-area aware.
 * Brand links home.
 */
const MobileNav: React.FC<MobileNavProps> = ({ left, right }) => {
  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-oled-bg/90 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-2xl items-center justify-between px-4 pt-[env(safe-area-inset-top)]">
        <div className="flex min-w-touch items-center">{left}</div>
        <Link
          to="/"
          className="flex items-center gap-2 font-bold tracking-wide text-oled-text [touch-action:manipulation]"
        >
          <Moon className="h-5 w-5 text-oled-cta" />
          <span>Dreams.ai</span>
        </Link>
        <div className="flex min-w-touch items-center justify-end">{right}</div>
      </div>
    </header>
  );
};

export default MobileNav;
