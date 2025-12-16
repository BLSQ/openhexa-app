import { WebappType } from "graphql/types";
import { i18n } from "next-i18next";

/**
 * Get the display label for a webapp type.
 * @param type - The webapp type enum value or string
 * @returns The human-readable label for the type
 */
export function getWebappTypeLabel(type: WebappType | string): string {
  switch (type) {
    case WebappType.Iframe:
      return i18n!.t("iFrame");
    case WebappType.Html:
      return i18n!.t("HTML");
    case WebappType.Bundle:
      return i18n!.t("Bundle");
    case WebappType.Superset:
      return i18n!.t("Superset");
    default:
      return String(type);
  }
}
