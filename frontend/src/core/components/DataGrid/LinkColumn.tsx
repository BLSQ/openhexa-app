import { ReactNode, useMemo } from "react";
import Link, { LinkProps } from "../Link";
import { BaseColumnProps } from "./BaseColumn";
import { useCellContext } from "./helpers";

type URLResolver = (value: any) => LinkProps["href"];
export type LinkColumnProps = Omit<BaseColumnProps, "children"> & {
  url: LinkProps["href"] | URLResolver;
  children?: ReactNode | ((value: any) => ReactNode);
} & Pick<LinkProps, "customStyle" | "className" | "noStyle">;

const LinkColumn = (props: LinkColumnProps) => {
  const { url, children, ...delegated } = props;
  const cell = useCellContext();

  const href = useMemo(() => {
    if (typeof url === "function") {
      return url(cell.value);
    } else {
      return url;
    }
  }, [cell.value, url]);

  return (
    <Link {...delegated} href={href}>
      {typeof children === "function" ? children(cell.value) : children}
    </Link>
  );
};

export default LinkColumn;
