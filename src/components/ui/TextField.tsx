import React, { useId } from "react";

interface TextFieldProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label: string;
  hideLabel?: boolean;
  error?: string | null;
}

/**
 * Multiline text field tuned for mobile: 16px font (prevents iOS zoom-on-focus),
 * visible focus ring, labelled for a11y.
 */
const TextField: React.FC<TextFieldProps> = ({
  label,
  hideLabel,
  error,
  className = "",
  id,
  ...rest
}) => {
  const generatedId = useId();
  const fieldId = id ?? generatedId;
  return (
    <div className="w-full">
      <label
        htmlFor={fieldId}
        className={
          hideLabel
            ? "sr-only"
            : "mb-2 block text-sm font-bold text-oled-text/80"
        }
      >
        {label}
      </label>
      <textarea
        id={fieldId}
        className={
          "w-full rounded-xl border border-white/15 bg-oled-primary px-4 py-3 " +
          "text-base text-oled-text placeholder:text-oled-text/40 " +
          "[touch-action:manipulation] resize-none transition-colors duration-200 " +
          "focus:border-oled-cta/60 focus:outline-none focus:ring-2 focus:ring-oled-cta/50 " +
          (error ? "border-oled-cta/70 " : "") +
          className
        }
        aria-invalid={error ? true : undefined}
        {...rest}
      />
      {error && (
        <p role="alert" className="mt-2 text-sm text-oled-cta">
          {error}
        </p>
      )}
    </div>
  );
};

export default TextField;
