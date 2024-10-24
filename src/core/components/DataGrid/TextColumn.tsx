import clsx from "clsx";
import get from "lodash/get";
import Link, { LinkProps } from "next/link";
import { ReactElement, useMemo } from "react";
import { BaseColumnProps } from "./BaseColumn";
import { useCellContext } from "./helpers";

type URLResolver = (value: any) => LinkProps["href"];
type TextColumnProps = BaseColumnProps & {
  url?: LinkProps["href"] | URLResolver;
  textPath?: string;
  symbolPath?: string;
  defaultValue?: ReactElement | string;
  subtextPath?: string;
  textClassName?: string;
};

export function TextColumn(props: TextColumnProps) {
  const {
    textPath,
    subtextPath,
    symbolPath,
    textClassName,
    url,
    defaultValue = "-",
  } = props;
  const cell = useCellContext();

  const text = useMemo(
    () => (textPath ? get(cell.value, textPath) : cell.value),
    [cell.value, textPath],
  );
  const subtext = useMemo(
    () => (subtextPath ? get(cell.value, subtextPath) : ""),
    [cell.value, subtextPath],
  );

  const symbol = useMemo(
    () => (symbolPath ? get(cell.value, symbolPath) : null),
    [cell.value, symbolPath],
  );

  const href = useMemo(() => {
    if (typeof url === "function") {
      return url(cell.value);
    } else {
      return url;
    }
  }, [cell.value, url]);

  const children = (
    <div className="flex max-w-full items-center gap-4">
      {symbol && (
        <div className="w-8">
          <img src={symbol} alt={text} />
        </div>
      )}
      <div className="truncate">
        <div
          title={text?.toString()}
          className={clsx("truncate lg:whitespace-nowrap", textClassName)}
        >
          {text ?? defaultValue}
        </div>
        {subtext && (
          <div className=" mt-1 truncate text-sm text-gray-400">{subtext}</div>
        )}
      </div>
    </div>
  );

  if (href) {
    return (
      <Link href={href} className="max-w-full">
        {children}
      </Link>
    );
  } else {
    return children;
  }
}
