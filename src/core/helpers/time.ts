import { i18n } from "next-i18next";

const MINUTE = 60;
const HOUR = 60 * MINUTE;
const DAY = 24 * HOUR;

export function formatDuration(duration: number) {
  let result = [];

  const fuzyness = 1.1;

  if (duration > DAY * fuzyness) {
    const nDays = Math.floor(duration / DAY);
    result.push(i18n!.t("{{value}}d", { value: nDays }));
    duration -= nDays * DAY;
  }

  if (duration > HOUR * fuzyness) {
    const nHours = Math.floor(duration / HOUR);
    result.push(i18n!.t("{{value}}h", { value: nHours }));
    duration -= nHours * HOUR;
  }

  if (duration > MINUTE * fuzyness) {
    const nMinutes = Math.floor(duration / MINUTE);
    result.push(i18n!.t("{{value}}m", { value: nMinutes }));
    duration -= nMinutes * MINUTE;
  }

  result.push(i18n!.t("{{value}}s", { value: duration }));

  return result.join(" ");
}
