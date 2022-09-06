import clsx from "clsx";
import _ from "lodash";
import Link, { LinkProps } from "next/link";
import { ReactElement, useMemo } from "react";
import { BaseColumnProps } from "./BaseColumn";
import { useCellContext } from "./helpers";

type URLResolver = (value: any) => LinkProps["href"];
type TextColumnProps = BaseColumnProps & {
  url?: LinkProps["href"] | URLResolver;
  textPath?: string;
  defaultValue?: ReactElement | string;
  subtextPath?: string;
  textClassName?: string;
};

export function TextColumn(props: TextColumnProps) {
  const {
    textPath,
    subtextPath,
    textClassName,
    url,
    defaultValue = "-",
  } = props;
  const cell = useCellContext();

  const text = useMemo(
    () => (textPath ? _.get(cell.value, textPath) : cell.value),
    [cell.value, textPath]
  );
  const subtext = useMemo(
    () => (subtextPath ? _.get(cell.value, subtextPath) : ""),
    [cell.value, subtextPath]
  );

  const href = useMemo(() => {
    if (typeof url === "function") {
      return url(cell.value);
    } else {
      return url;
    }
  }, [cell.value, url]);

  const children = (
    <div className="w-full">
      <div
        title={text}
        className={clsx("truncate lg:whitespace-nowrap", textClassName)}
      >
        {text ?? defaultValue}
      </div>
      {subtext && (
        <div className=" mt-1 truncate text-sm text-gray-400">{subtext}</div>
      )}
    </div>
  );

  if (href) {
    return (
      <Link href={href}>
        <a>{children}</a>
      </Link>
    );
  } else {
    return children;
  }
}
