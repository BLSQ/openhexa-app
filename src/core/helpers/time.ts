import { i18n } from "next-i18next";

const MINUTE = 60;
const HOUR = 60 * MINUTE;
const DAY = 24 * HOUR;

export function formatDuration(duration: number, fuzziness: number = 1.1) {
  let result = [];

  if (duration > DAY * fuzziness) {
    const nDays = Math.floor(duration / DAY);
    result.push(i18n!.t("{{value}}d", { value: nDays }));
    duration -= nDays * DAY;
  }

  if (duration > HOUR * fuzziness) {
    const nHours = Math.floor(duration / HOUR);
    if (nHours > 0) {
      result.push(i18n!.t("{{value}}h", { value: nHours }));
      duration -= nHours * HOUR;
    }
  }

  if (duration > MINUTE * fuzziness) {
    const nMinutes = Math.floor(duration / MINUTE);
    if (nMinutes > 0) {
      result.push(i18n!.t("{{value}}m", { value: nMinutes }));
      duration -= nMinutes * MINUTE;
    }
  }

  result.push(i18n!.t("{{value}}s", { value: duration }));

  return result.join(" ");
}
