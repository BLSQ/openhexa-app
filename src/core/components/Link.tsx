import type { LinkProps as NextLinkProps } from "next/link";
import NextLink from "next/link";
import Anchor, { AnchorProps } from "./Anchor";

type LinkProps = Omit<AnchorProps, "href"> & {
  customStyle?: string;
  className?: string;
} & NextLinkProps;

const Link = (props: LinkProps) => {
  const { children, linkStyle, className, ...delegated } = props;
  return (
    <NextLink {...delegated}>
      <Anchor linkStyle={linkStyle} className={className}>
        {children}
      </Anchor>
    </NextLink>
  );
};

export default Link;
