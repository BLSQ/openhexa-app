import { DateTimeOptions } from "luxon";
import Time from "../Time";
import { BaseColumnProps } from "./BaseColumn";
import { useCellContext } from "./helpers";

type DateColumnProps = {
  format?: DateTimeOptions;
  defaultValue?: string;
} & BaseColumnProps;

const DateColumn = ({
  className,
  format,
  defaultValue = "-",
}: DateColumnProps) => {
  const cell = useCellContext();

  if (!cell.value) {
    return defaultValue ? <span>{defaultValue}</span> : null;
  }
  return <Time className={className} datetime={cell.value} format={format} />;
};

export default DateColumn;
