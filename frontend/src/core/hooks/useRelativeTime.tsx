import { DateTime } from "luxon";
import { useMemo, useState } from "react";
import useInterval from "./useInterval";

function useRelativeTime(datetime: DateTime | string) {
  const [isToggled, setToggled] = useState(false);
  useInterval(() => setToggled(!isToggled), 5000);

  const value = useMemo(() => {
    if (!datetime) return null;
    return typeof datetime === "string"
      ? DateTime.fromISO(datetime, { zone: "utc" })
      : datetime;
  }, [datetime]);

  return value ? value.toRelative() : null;
}

export default useRelativeTime;
