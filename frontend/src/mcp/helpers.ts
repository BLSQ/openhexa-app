import { TFunction } from "next-i18next";

export function getMCPErrorMessage(t: TFunction, errors?: string[]): string {
  const messages: Record<string, string> = {
    CLIENT_NOT_FOUND: t(
      "This application is no longer registered. Connect it again from your MCP client.",
    ),
    NOT_FOUND: t("This connection no longer exists. Reload the page."),
    TOOL_NOT_FOUND: t(
      "Some selected tools are no longer available. Reload the page and try again.",
    ),
    WORKSPACE_NOT_FOUND: t(
      "You no longer have access to one of the selected workspaces. Reload the page and try again.",
    ),
  };
  const code = errors?.find((error) => error in messages);
  return code ? messages[code] : t("An error occurred. Please try again.");
}
