import React from "react";

type Variant = "cta" | "secondary" | "ghost";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  fullWidth?: boolean;
  loading?: boolean;
}

const base =
  "inline-flex items-center justify-center gap-2 rounded-xl font-bold tracking-wide " +
  "min-h-touch px-6 py-3 select-none cursor-pointer " +
  "[touch-action:manipulation] transition-[opacity,transform,background-color] duration-200 " +
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-oled-cta focus-visible:ring-offset-2 focus-visible:ring-offset-oled-bg " +
  "disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98] motion-reduce:active:scale-100";

const variants: Record<Variant, string> = {
  cta: "bg-oled-cta text-white hover:opacity-90 shadow-[0_4px_18px_rgba(225,29,72,0.35)]",
  secondary:
    "bg-oled-primary text-oled-text border border-white/15 hover:border-white/30",
  ghost: "bg-transparent text-oled-text/80 hover:text-oled-text hover:bg-white/5",
};

const Button: React.FC<ButtonProps> = ({
  variant = "cta",
  fullWidth,
  loading,
  className = "",
  children,
  disabled,
  ...rest
}) => {
  return (
    <button
      className={`${base} ${variants[variant]} ${fullWidth ? "w-full" : ""} ${className}`}
      disabled={disabled || loading}
      {...rest}
    >
      {loading && (
        <span
          aria-hidden="true"
          className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent motion-reduce:animate-none"
        />
      )}
      {children}
    </button>
  );
};

export default Button;
