import clsx from "clsx";
import { ButtonHTMLAttributes, ReactElement, ReactNode } from "react";

const ButtonVariants = [
  "primary",
  "secondary",
  "white",
  "danger",
  "outlined",
  "custom",
] as const;
type ButtonVariant = (typeof ButtonVariants)[number];

const ButtonSizes = ["sm", "md", "lg", "xl", "xxl"] as const;
type ButtonSize = (typeof ButtonSizes)[number];

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  className?: string;
  leadingIcon?: ReactNode;
  type?: "button" | "submit" | "reset";
  rounded?: boolean;
  focusRing?: boolean;
}

export const Classes: { [key: string]: string } = {
  base: `relative h-fit
    inline-flex items-center justify-center transition-all
    border font-medium
    disabled:opacity-50 disabled:cursor-not-allowed
  `,
  primary:
    "shadow-xs border-transparent text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500",
  secondary:
    "shadow-xs border-transparent text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:ring-indigo-500",
  white:
    "shadow-xs text-gray-800 border-gray-400 bg-white hover:bg-gray-50 focus:ring-gray-400",
  outlined: "text-gray-800 border-transparent hover:bg-gray-100",
  danger:
    "shadow-xs border-transparent text-white bg-red-600 hover:bg-red-700 focus:ring-red-600",

  // Sizes
  sm: "text-xs px-2 py-1",
  md: "text-sm px-3 py-2.5 leading-4",
  lg: "text-sm px-4 py-2.5",
  xl: "text-base px-4 py-2",
  xxl: "text-base px-6 py-3",
};

const Button = (props: ButtonProps) => {
  const {
    variant = "primary",
    size = "md",
    className,
    children,
    leadingIcon,
    disabled,
    type = "button",
    rounded = true,
    focusRing = true,
    ...delegated
  } = props;

  const classes = clsx(
    Classes.base,
    rounded && "rounded-sm",
    focusRing && "focus:outline-hidden focus:ring-2 focus:ring-offset-2",
    Classes[size],
    variant !== "custom" && Classes[variant],
    className,
  );
  return (
    <button className={classes} disabled={disabled} type={type} {...delegated}>
      {leadingIcon ? (
        <LeadingIcon size={size}>{leadingIcon}</LeadingIcon>
      ) : null}
      {children}
    </button>
  );
};
Button.Variants = ButtonVariants;
Button.Sizes = ButtonSizes;

const LeadingIcon = (props: { children: ReactNode; size?: ButtonSize }) => {
  return (
    <div
      className={clsx(
        "-ml-1",
        props.size === ButtonSizes[0] ? "mr-1" : "mr-1.5",
      )}
      aria-hidden="true"
    >
      {props.children}
    </div>
  );
};

export default Button;
