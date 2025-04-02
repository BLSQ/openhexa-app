import clsx from "clsx";
import type { LinkProps as NextLinkProps } from "next/link";
import NextLink from "next/link";
import { AnchorProps } from "./Anchor";

export type LinkProps = Omit<AnchorProps, "href"> & {
  customStyle?: string;
  className?: string;
  noStyle?: boolean;
  rel?: string;
} & NextLinkProps;

const Link = (props: LinkProps) => {
  const {
    children,
    className,
    customStyle,
    noStyle = false,
    rel = "noopener noreferrer",
    ...delegated
  } = props;
  return (
    <NextLink
      {...delegated}
      rel={rel}
      className={clsx(
        className,
        !noStyle && (customStyle ?? "text-blue-600 hover:text-blue-500"),
      )}
    >
      {children}
    </NextLink>
  );
};

export default Link;
