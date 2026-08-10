import { remark } from "remark";
import strip from "strip-markdown";
import { validate as validateUuid } from "uuid";

export function isValidUuid(value: unknown): value is string {
  return typeof value === "string" && validateUuid(value);
}

export function isValidUrl(url: string) {
  try {
    new URL(url);
    return true;
  } catch (error) {
    return false;
  }
}

export function stripMarkdown(markdown: string): string {
  /*
  Strip markdown and returns the plain text
  */
  return remark().use(strip).processSync(markdown).toString();
}
