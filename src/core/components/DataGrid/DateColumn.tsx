import { DateTimeOptions } from "luxon";
import Time from "../Time";
import { BaseColumnProps } from "./BaseColumn";
import { useCellContext } from "./helpers";

type DateColumnProps = {
  format?: DateTimeOptions;
  relative?: boolean;
  defaultValue?: string;
} & BaseColumnProps;

const DateColumn = ({
  format,
  relative,
  defaultValue = "-",
}: DateColumnProps) => {
  const cell = useCellContext();

  if (!cell.value) {
    return defaultValue ? <span>{defaultValue}</span> : null;
  }
  return (
    <Time
      className="truncate"
      datetime={cell.value}
      format={format}
      relative={relative}
    />
  );
};

export default DateColumn;
