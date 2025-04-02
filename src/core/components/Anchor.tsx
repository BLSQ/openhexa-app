import clsx from "clsx";
import { AnchorHTMLAttributes, forwardRef, ReactNode } from "react";

export type AnchorProps = AnchorHTMLAttributes<HTMLAnchorElement> & {
  linkStyle?: string;
  children?: ReactNode;
};

const Anchor = forwardRef<HTMLAnchorElement, AnchorProps>((props, ref) => {
  const {
    linkStyle = "text-blue-600 hover:text-blue-500",
    className,
    ...delegated
  } = props;
  return (
    <a
      ref={ref}
      className={clsx(className, linkStyle, "cursor-pointer outline-hidden")}
      {...delegated}
    />
  );
});

export default Anchor;
