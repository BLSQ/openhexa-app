import { Locator, Page, expect } from "@playwright/test";

import {
  AssistantPanel,
  TURN_TIMEOUT,
  proposeThenExplainPrompt,
} from "./AssistantPanel";

/** What `ASSISTANT_PIPELINE_SOURCE` logs before the assistant changes it. */
export const ORIGINAL_LOG_MESSAGE = "E2E-ORIGINAL-MESSAGE";

/**
 * A one-line pipeline, so the change asked of the assistant is unambiguous and
 * shows on screen without scrolling the editor.
 */
export const ASSISTANT_PIPELINE_SOURCE = `from openhexa.sdk import current_run, pipeline


@pipeline("e2e_assistant", name="E2E assistant pipeline")
def e2e_assistant():
    current_run.log_info("${ORIGINAL_LOG_MESSAGE}")


if __name__ == "__main__":
    e2e_assistant()
`;

export function logMessageChangePrompt(message: string): string {
  return proposeThenExplainPrompt(
    `In pipeline.py, change the message passed to current_run.log_info to exactly "${message}"`,
    "propose_pipeline_version",
  );
}

/**
 * Asks for the pipeline under an exact name: a pipeline's code is its name
 * slugified, so a lowercase, hyphenated name is also the code the test cleans
 * up -- known before the agent has created anything.
 */
export function createPipelinePrompt(name: string, message: string): string {
  return [
    `Create a pipeline named exactly "${name}".`,
    `Its pipeline.py only logs the message "${message}" with current_run.log_info.`,
    "It has no parameters and no other files. Do not ask me any questions.",
  ].join(" ");
}

/** The AI assistant on a pipeline's Code tab. */
export class PipelineAssistantPanel extends AssistantPanel {
  constructor(page: Page) {
    super(page, {
      proposal: "Proposed version from AI assistant",
      messagePlaceholder: "Version description",
    });
  }

  /** Save only shows while there are pending changes, so it goes on publish. */
  protected async expectSaved() {
    await expect(this.saveButton).toBeHidden();
  }
}

/** The "Create with AI" path of the pipelines page's Create dialog. */
export class CreatePipelineWithAIDialog {
  constructor(private readonly page: Page) {}

  get openButton(): Locator {
    return this.page.getByRole("button", { name: "Create", exact: true });
  }

  get dialog(): Locator {
    return this.page.getByRole("dialog");
  }

  get title(): Locator {
    return this.dialog.getByRole("heading", { name: "Create with AI" });
  }

  /** The method card's name also carries its description. */
  get methodButton(): Locator {
    return this.dialog.getByRole("button", { name: /^Create with AI/ });
  }

  get promptInput(): Locator {
    return this.dialog.getByRole("textbox");
  }

  get submitButton(): Locator {
    return this.dialog.getByRole("button", { name: "Create", exact: true });
  }

  step(label: string): Locator {
    return this.dialog.getByText(label);
  }

  async open() {
    await this.openButton.click();
    await this.methodButton.click();
    await expect(this.title).toBeVisible();
  }

  /** Sends the prompt; the dialog then redirects to the new pipeline's code. */
  async submit(prompt: string) {
    await this.promptInput.fill(prompt);
    await this.submitButton.click();
  }

  /** Waits for the redirect to the new pipeline's Code tab. Returns its code. */
  async waitForPipeline(): Promise<string> {
    await this.page.waitForURL(/\/pipelines\/[^/]+\/code\/?$/, {
      timeout: TURN_TIMEOUT,
    });
    return this.page.url().replace(/\/code\/?$/, "").split("/pipelines/")[1];
  }
}
