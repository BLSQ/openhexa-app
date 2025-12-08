import { WebappType } from "graphql/types";

/**
 * Get the display label for a webapp type.
 * @param type - The webapp type enum value or string
 * @returns The human-readable label for the type
 */
export function getWebappTypeLabel(type: WebappType | string): string {
  switch (type) {
    case WebappType.Iframe:
    case "IFRAME":
      return "iFrame";
    case WebappType.Html:
    case "HTML":
      return "HTML";
    case WebappType.Bundle:
    case "BUNDLE":
      return "Bundle";
    case WebappType.Superset:
    case "SUPERSET":
      return "Superset";
    default:
      return String(type);
  }
}
