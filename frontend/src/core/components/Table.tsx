import clsx from "clsx";
import { HTMLAttributes } from "react";

export const TableClasses = {
  table: "w-full divide-y divide-gray-200 ",
  thead: "",
  tbody: "divide-y divide-gray-200",
  tr: "",
  th: "bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
  td: "text-sm text-gray-500 h-full",
};

const SpacingClasses = {
  td: {
    tight: "px-2 py-2 first:pl-4 last:pr-4",
    loose: "px-4 py-3 first:pl-6 last:pr-6",
  },

  th: {
    tight: "px-2 py-2 first:pl-4 last:pr-4",
    loose: "px-4 py-5 first:pl-6 last:pr-6",
  },
};

export const Table = (props: HTMLAttributes<HTMLTableElement>) => (
  <table {...props} className={props.className ?? TableClasses.table} />
);

export const TableHead = (props: HTMLAttributes<HTMLTableSectionElement>) => (
  <thead className={props.className ?? TableClasses.thead} {...props} />
);

export const TableBody = (props: HTMLAttributes<HTMLTableSectionElement>) => (
  <tbody className={props.className ?? TableClasses.tbody} {...props} />
);

export const TableRow = (props: HTMLAttributes<HTMLTableRowElement>) => (
  <tr className={props.className ?? TableClasses.tr} {...props} />
);

export type TableCellProps = HTMLAttributes<HTMLTableCellElement> & {
  width?: string;
  heading?: boolean;
  wrap?: boolean;
  spacing?: "tight" | "loose";
  overrideStyle?: boolean;
};

export const TableCell = (props: TableCellProps) => {
  const {
    heading = false,
    wrap = false,
    overrideStyle = false,
    className,
    spacing = "loose",
    children,
    width,
    ...delegated
  } = props;
  const Elm = heading ? "th" : "td";
  const extraProps: { [key: string]: any } = {};

  if (heading) {
    extraProps.scope = "col";
  }

  return (
    <Elm
      {...extraProps}
      {...delegated}
      width={width}
      className={clsx(
        overrideStyle ? className : TableClasses[Elm],
        !overrideStyle && className,
        SpacingClasses[Elm][spacing],
        !wrap && "whitespace-nowrap",
      )}
    >
      {children}
    </Elm>
  );
};
