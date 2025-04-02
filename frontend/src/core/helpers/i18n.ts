import { IncomingHttpHeaders } from "http";

export const LANGUAGES = {
  en: "English",
  fr: "Français",
};

export function getAcceptPreferredLocale(headers: IncomingHttpHeaders) {
  if (headers["accept-language"]) {
    try {
      const langs = headers["accept-language"]
        .split(",")
        .map((lang) => lang.split(";")[0].split("-")[0])
        .filter((lang) => lang in LANGUAGES);
      return langs[0];
    } catch (err) {
      return "en";
    }
  }
}
