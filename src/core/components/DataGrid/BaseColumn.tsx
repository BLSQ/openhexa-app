import { ReactElement } from "react";
import { UseTableColumnOptions } from "react-table";
import { useCellContext } from "./helpers";

export type BaseColumnProps = { [key: string]: any } & {
  id?: string;
  label?: string;
  header?: UseTableColumnOptions<any>["Header"];
  hideLabel?: boolean;
  accessor?: string | ((value: any) => any);
  className?: string;
  headerClassName?: string;
  minWidth?: number;
  width?: number;
  maxWidth?: number;
};

type ColumnProps<V = any> = BaseColumnProps & {
  children: (value: V) => ReactElement | null;
};

export function BaseColumn<V = any>({ children }: ColumnProps<V>) {
  const cell = useCellContext<V>();
  return children(cell.value);
}
