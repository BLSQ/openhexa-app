import { Page, expect } from "@playwright/test";

import { AssistantPanel, proposeThenExplainPrompt } from "./AssistantPanel";
import { CreateWithAIDialog } from "./CreateWithAIDialog";

export function headingChangePrompt(heading: string): string {
  return proposeThenExplainPrompt(
    `In index.html, change the text of the <h1> heading to exactly "${heading}"`,
    "propose_webapp_version",
  );
}

/**
 * Asks for the app under an exact name: a web app's slug is its name slugified,
 * so a lowercase, hyphenated name is also the slug the test cleans up -- known
 * before the agent has created anything. The app reads the workspace database
 * through a saved query the test made beforehand, which the agent is told to
 * reuse rather than write one of its own.
 */
export function createWebappPrompt(
  name: string,
  heading: string,
  savedQuerySlug: string,
): string {
  return [
    `Create a static web app named exactly "${name}".`,
    `Its index.html shows the heading "${heading}" in an <h1>, then a table of the rows returned by the existing saved query whose slug is "${savedQuerySlug}" (columns: code and name), run through executeSavedQuery.`,
    "Reuse that saved query as it is: do not create or change any saved query.",
    "Keep everything in a single index.html file. Do not ask me any questions.",
  ].join(" ");
}

/** The "Create with AI" path of the web apps page's Create dialog. */
export class CreateWebappWithAIDialog extends CreateWithAIDialog {
  /** Waits for the redirect to the new app's Code tab. Returns its slug. */
  waitForWebapp(): Promise<string> {
    return this.waitForEditor("webapps");
  }
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
