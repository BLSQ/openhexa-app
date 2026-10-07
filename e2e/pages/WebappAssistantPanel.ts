import { Page, expect } from "@playwright/test";

import { AssistantPanel, proposeThenExplainPrompt } from "./AssistantPanel";

export function headingChangePrompt(heading: string): string {
  return proposeThenExplainPrompt(
    `In index.html, change the text of the <h1> heading to exactly "${heading}"`,
    "propose_webapp_version",
  );
}

/** The AI assistant on a static web app's Code tab. */
export class WebappAssistantPanel extends AssistantPanel {
  constructor(page: Page) {
    super(page, {
      proposal: "Proposed changes from AI assistant",
      messagePlaceholder: "Commit message",
    });
  }

  protected async expectSaved() {
    await expect(
      this.page.getByText("Web app saved successfully", { exact: true }),
    ).toBeVisible();
  }
}
