import NextLink from "next/link";
import type { LinkProps as NextLinkProps } from "next/link";
import { ReactNode } from "react";
import clsx from "clsx";

type LinkProps = {
  color?: string;
  hoverColor?: string;
  customStyle?: string;
  className?: string;
  children?: ReactNode;
} & NextLinkProps;

const Link = (props: LinkProps) => {
  const { children, className, color, hoverColor, ...delegated } = props;
  return (
    <NextLink {...delegated}>
      <a
        className={clsx(
          "cursor-pointer outline-none",
          className,
          color ?? "text-blue-600",
          hoverColor ? `hover:${hoverColor}` : "hover:text-blue-500"
        )}
      >
        {children}
      </a>
    </NextLink>
  );
};

export default Link;
