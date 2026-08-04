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
    // All dates from the backend are in UTC, but some (e.g. pipeline run message
    // timestamps) carry no offset. Defaulting the zone to UTC keeps those from
    // being read as local time; strings with an explicit offset are unaffected.
    () => DateTime.fromISO(props.datetime, { zone: "utc" }).toLocal(),
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
