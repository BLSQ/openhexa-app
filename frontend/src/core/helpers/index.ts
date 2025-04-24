import { remark } from "remark";
import strip from "strip-markdown";

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
