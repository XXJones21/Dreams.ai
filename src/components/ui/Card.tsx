import React from "react";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  as?: keyof JSX.IntrinsicElements;
}

/** Minimal OLED surface card: deep-primary fill, hairline border, soft radius. */
const Card: React.FC<CardProps> = ({ as: Tag = "div", className = "", children, ...rest }) => {
  const Comp = Tag as React.ElementType;
  return (
    <Comp
      className={
        "rounded-2xl border border-white/10 bg-oled-primary p-5 " + className
      }
      {...rest}
    >
      {children}
    </Comp>
  );
};

export default Card;
