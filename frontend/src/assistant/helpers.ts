import { TFunction } from "next-i18next";

export function getErrorCodeMessage(t: TFunction, errorCode?: string): string {
  const messages: Record<string, string> = {
    AGENT_STUCK_IN_LOOP: t(
      "I got stuck in a loop — try breaking your request into smaller steps.",
    ),
    MAX_TOKENS_REACHED: t(
      "I hit the maximum token limit — try breaking your request into smaller steps.",
    ),
    UNEXPECTED_MODEL_BEHAVIOR: t("An unexpected error occurred. Please try again."),
    UNKNOWN_ERROR: t("An error occurred. Please try again."),
  };
  return (
    (errorCode && messages[errorCode]) ??
    t("The AI service encountered an error. Please try again.")
  );
}
