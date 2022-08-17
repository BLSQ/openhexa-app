import { ReactElement } from "react";
import { useCellContext } from "./helpers";

export type BaseColumnProps = { [key: string]: any } & {
  id?: string;
  label?: string;
  hideLabel?: boolean;
  accessor?: string;
  className?: string;
  headerClassName?: string;
  cell?: any;
  minWidth?: number;
  width?: number;
  maxWidth?: number;
  children?: (value: any) => ReactElement;
};

export function BaseColumn({ children, className }: BaseColumnProps) {
  const cell = useCellContext();

  if (children) {
    return children(cell.value);
  } else {
    return <span className="truncate">{cell.value}</span>;
  }
}
