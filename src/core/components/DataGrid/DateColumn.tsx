import { DateTimeOptions } from "luxon";
import Time from "../Time";
import { BaseColumnProps } from "./BaseColumn";
import { useCellContext } from "./helpers";

type DateColumnProps = {
  format?: DateTimeOptions;
} & BaseColumnProps;

const DateColumn = (props: DateColumnProps) => {
  const cell = useCellContext();

  return (
    <Time
      className={props.className}
      datetime={cell.value}
      format={props.format}
    />
  );
};

export default DateColumn;
