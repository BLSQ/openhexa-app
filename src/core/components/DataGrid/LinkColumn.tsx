import { LinkProps } from "next/link";
import { ReactNode, useMemo } from "react";
import Link from "../Link";
import { BaseColumnProps } from "./BaseColumn";
import { useCellContext } from "./helpers";

type URLResolver = (value: any) => LinkProps["href"];
export type LinkColumnProps = Omit<BaseColumnProps, "children"> & {
  url: LinkProps["href"] | URLResolver;
  linkStyle?: string;
  children?: ReactNode;
};

const LinkColumn = (props: LinkColumnProps) => {
  const { className, url, children, linkStyle } = props;
  const cell = useCellContext();

  const href = useMemo(() => {
    if (typeof url === "function") {
      return url(cell.value);
    } else {
      return url;
    }
  }, [cell.value, url]);

  return (
    <Link className={className} linkStyle={linkStyle} href={href}>
      {children}
    </Link>
  );
};

export default LinkColumn;
