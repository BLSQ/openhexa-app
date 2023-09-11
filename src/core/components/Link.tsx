import clsx from "clsx";
import type { LinkProps as NextLinkProps } from "next/link";
import NextLink from "next/link";
import { AnchorProps } from "./Anchor";

export type LinkProps = Omit<AnchorProps, "href"> & {
  customStyle?: string;
  className?: string;
  noStyle?: boolean;
} & NextLinkProps;

const Link = (props: LinkProps) => {
  const {
    children,
    className,
    customStyle,
    noStyle = false,
    ...delegated
  } = props;
  return (
    <NextLink
      {...delegated}
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
