import { LinkProps } from "next/link";
import { ReactNode, useMemo } from "react";
import Link from "../Link";
import { BaseColumnProps } from "./BaseColumn";
import { useCellContext } from "./helpers";

type URLResolver = (value: any) => LinkProps["href"];
export type LinkColumnProps = Omit<BaseColumnProps, "children"> & {
  url: LinkProps["href"] | URLResolver;
  hoverColor?: string;
  children?: ReactNode;
  color?: string;
};

const LinkColumn = (props: LinkColumnProps) => {
  const { className, url, children, hoverColor, color } = props;
  const cell = useCellContext();

  const href = useMemo(() => {
    if (typeof url === "function") {
      return url(cell.value);
    } else {
      return url;
    }
  }, [cell.value, url]);

  return (
    <Link
      className={className}
      hoverColor={hoverColor}
      color={color}
      href={href}
    >
      {children}
    </Link>
  );
};

export default LinkColumn;
