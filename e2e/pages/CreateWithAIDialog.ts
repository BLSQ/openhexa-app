import { Locator, Page, expect } from "@playwright/test";

import { TURN_TIMEOUT } from "./AssistantPanel";

/**
 * The "Create with AI" path of a Create dialog, which the pipelines and the
 * web apps pages share: a prompt, the agent's progress, then a redirect to the
 * new object's code editor.
 */
export abstract class CreateWithAIDialog {
  constructor(protected readonly page: Page) {}

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

  /** Sends the prompt; the dialog then redirects to the new object's code. */
  async submit(prompt: string) {
    await this.promptInput.fill(prompt);
    await this.submitButton.click();
  }

  /** Waits for the redirect to the Code tab. Returns the code or slug. */
  protected async waitForEditor(
    section: "pipelines" | "webapps",
  ): Promise<string> {
    await this.page.waitForURL(new RegExp(`/${section}/[^/]+/code/?$`), {
      timeout: TURN_TIMEOUT,
    });
    return this.page.url().replace(/\/code\/?$/, "").split(`/${section}/`)[1];
  }
}
