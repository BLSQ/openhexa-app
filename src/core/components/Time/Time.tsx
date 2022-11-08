import clsx from "clsx";
import useInterval from "core/hooks/useInterval";
import useRelativeTime from "core/hooks/useRelativeTime";
import { DateTime, DateTimeOptions } from "luxon";
import { memo, useEffect, useMemo, useState } from "react";

type Props = {
  datetime: string;
  className?: string;
  relative?: boolean;
  format?: DateTimeOptions;
};

const Time = (props: Props) => {
  const datetime = useMemo(
    () => DateTime.fromISO(props.datetime),
    [props.datetime]
  );

  const relativeDate = useRelativeTime(datetime);

  const value = useMemo(() => {
    if (props.relative) {
      return relativeDate;
    } else {
      return datetime.toLocaleString(props.format ?? DateTime.DATETIME_SHORT);
    }
    // We use the toggle variable to force React to recompute this value
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [datetime, props.format, props.relative, relativeDate]);

  return (
    <time
      /* Relative time can quickly change between the server rendering and the client rendering. Let's ignore this while hydrating the dom */
      suppressHydrationWarning={props.relative}
      title={datetime.toISO()}
      dateTime={datetime.toISO()}
      className={clsx("whitespace-nowrap", props.className)}
    >
      {value}
    </time>
  );
};

export default memo(Time);
