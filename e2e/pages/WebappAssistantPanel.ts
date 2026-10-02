import { Locator, Page, expect } from "@playwright/test";

/** Shown on Save and Dismiss while a proposal cannot be resolved yet. */
export const WAITING_FOR_ASSISTANT = "Waiting for the assistant to finish…";

/** A full turn -- reading the files, proposing, then writing -- is slow. */
const TURN_TIMEOUT = 180_000;

/**
 * Asks for an exact, checkable edit, then for a long answer after it: the
 * proposal can only be resolved once the turn ends, and that tail of writing
 * keeps the turn open long enough to see Save and Dismiss refused meanwhile.
 */
export function headingChangePrompt(heading: string): string {
  return [
    `In index.html, change the text of the <h1> heading to exactly "${heading}" and change nothing else.`,
    "Propose the change with propose_webapp_version first.",
    "Only after proposing it, explain the change in a detailed answer of at least 200 words.",
  ].join(" ");
}

/** The AI assistant on a static web app's Code tab. */
export class WebappAssistantPanel {
  constructor(private readonly page: Page) {}

  get openButton(): Locator {
    return this.page.getByRole("button", { name: "AI Assistant" });
  }

  get heading(): Locator {
    return this.page.getByRole("heading", { name: "AI Assistant", level: 3 });
  }

  get messageInput(): Locator {
    return this.page.getByPlaceholder(
      "Message… (Enter to send, Shift+Enter for newline)",
    );
  }

  /** A message bubble in the conversation. */
  message(text: string): Locator {
    return this.page.getByText(text, { exact: true });
  }

  get proposalBanner(): Locator {
    return this.page.getByText("Proposed changes from AI assistant");
  }

  get dismissButton(): Locator {
    return this.page.getByRole("button", { name: "Dismiss" });
  }

  get commitMessageInput(): Locator {
    return this.page.getByPlaceholder("Commit message");
  }

  /** The editor's own Save, which accepts a proposal. */
  get saveButton(): Locator {
    return this.page.getByRole("button", { name: "Save", exact: true });
  }

  async open() {
    await this.openButton.click();
    await expect(this.heading).toBeVisible();
  }

  /** The send button has no accessible name; Enter sends, as users do. */
  async send(text: string) {
    await this.messageInput.fill(text);
    await this.messageInput.press("Enter");
    await expect(this.message(text)).toBeVisible();
  }

  /**
   * Waits for a proposal and checks it cannot be resolved while the agent is
   * still writing, then waits for the turn to end and for that to lift.
   */
  async waitForProposal() {
    await expect(this.proposalBanner).toBeVisible({ timeout: TURN_TIMEOUT });

    for (const button of [this.dismissButton, this.saveButton]) {
      await expect(button).toBeDisabled();
      await expect(button).toHaveAttribute("title", WAITING_FOR_ASSISTANT);
    }

    await expect(this.dismissButton).toBeEnabled({ timeout: TURN_TIMEOUT });
    await expect(this.saveButton).toBeEnabled();
  }

  async dismiss() {
    await this.dismissButton.click();
    await expect(this.proposalBanner).toBeHidden();
  }

  /** Saves the proposal under `commitMessage`, which commits and publishes it. */
  async accept(commitMessage: string) {
    await this.commitMessageInput.fill(commitMessage);
    await this.saveButton.click();
    await expect(
      this.page.getByText("Web app saved successfully", { exact: true }),
    ).toBeVisible();
    await expect(this.proposalBanner).toBeHidden();
  }
}
