import clsx from "clsx";
import type { LinkProps as NextLinkProps } from "next/link";
import NextLink from "next/link";
import { AnchorProps } from "./Anchor";

type LinkProps = Omit<AnchorProps, "href"> & {
  customStyle?: string;
  className?: string;
} & NextLinkProps;

const Link = (props: LinkProps) => {
  const { children, className, customStyle, ...delegated } = props;
  return (
    <NextLink
      {...delegated}
      className={clsx(
        className,
        customStyle ?? "text-blue-600 hover:text-blue-500"
      )}
    >
      {children}
    </NextLink>
  );
};

export default Link;
