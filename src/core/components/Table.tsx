import clsx from "clsx";
import { HTMLAttributes } from "react";

export const TableClasses = {
  table: "w-full divide-y divide-gray-200 ",
  thead: "",
  tbody: "divide-y divide-gray-200",
  tr: "",
  th: "px-4 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider first:pl-6 last:pr-6",
  td: "px-4 py-5 text-sm text-gray-500 h-full first:pl-6 last:pr-6",
};

export const Table = (props: HTMLAttributes<HTMLTableElement>) => (
  <table {...props} className={clsx(props.className, TableClasses.table)} />
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

export const TableCell = (
  props: HTMLAttributes<HTMLTableCellElement> & {
    width?: string;
    heading?: boolean;
    wrap?: boolean;

    overrideStyle?: boolean;
  },
) => {
  const {
    heading = false,
    wrap = false,
    overrideStyle = false,
    className,
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
        !wrap && "whitespace-nowrap",
      )}
    >
      {children}
    </Elm>
  );
};
