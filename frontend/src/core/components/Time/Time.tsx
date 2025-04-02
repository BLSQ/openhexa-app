import clsx from "clsx";
import useRelativeTime from "core/hooks/useRelativeTime";
import { DateTime, DateTimeOptions } from "luxon";
import { useMemo } from "react";

type Props = {
  datetime: string;
  className?: string;
  relative?: boolean;
  format?: DateTimeOptions;
};

const Time = (props: Props) => {
  const datetime = useMemo(
    // By default, all dates from the backend are in UTC
    () => DateTime.fromISO(props.datetime).toLocal(),
    [props.datetime],
  );

  const relativeDate = useRelativeTime(datetime);

  if (!datetime?.isValid) return null;

  const isoDate = datetime.toISO();
  return (
    <time
      suppressHydrationWarning={true}
      title={isoDate ?? undefined}
      dateTime={isoDate ?? undefined}
      className={clsx("whitespace-nowrap", props.className)}
    >
      {props.relative
        ? relativeDate
        : datetime.toLocaleString(props.format ?? DateTime.DATETIME_SHORT)}
    </time>
  );
};

export default Time;
