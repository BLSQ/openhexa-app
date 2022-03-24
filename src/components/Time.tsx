import { DateTime, DateTimeOptions } from "luxon";
import { memo } from "react";

type Props = {
  datetime: string;
  className?: string;
  format?: DateTimeOptions;
};

const Time = (props: Props) => {
  const datetime = DateTime.fromISO(props.datetime);

  return (
    <time
      title={datetime.toISO()}
      dateTime={datetime.toISO()}
      className={props.className}
    >
      {datetime.toLocaleString(props.format ?? DateTime.DATETIME_SHORT)}
    </time>
  );
};

export default memo(Time);
