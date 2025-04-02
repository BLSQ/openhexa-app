import clsx from "clsx";
import { HTMLAttributes } from "react";

export type AvatarProps = {
  initials: string;
  size?: "xs" | "sm" | "md" | "lg" | "xl";
  color?: string;
} & HTMLAttributes<HTMLSpanElement>;

const Avatar = (props: AvatarProps) => {
  const { initials, color, size = "md", ...delegated } = props;

  let className;
  switch (size) {
    case "xs":
      className = "text-xs h-6 w-6";
      break;
    case "sm":
      className = "text-sm h-8 w-8";
      break;
    case "md":
      className = "text-md h-10 w-10";
      break;
    case "lg":
      className = "text-lg h-12 w-12";
      break;
    case "xl":
      className = "text-xl h-14 w-14";
      break;
  }

  return (
    <span
      {...delegated}
      style={{ background: color }}
      className={clsx(
        "inline-flex shrink-0 items-center justify-center rounded-full bg-gray-500",
        className,
      )}
    >
      <span className="font-medium leading-none text-white">{initials}</span>
    </span>
  );
};

export default Avatar;
