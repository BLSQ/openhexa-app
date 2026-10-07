import { Locator, Page, expect } from "@playwright/test";

/** Shown on Save and Dismiss while a proposal cannot be resolved yet. */
export const WAITING_FOR_ASSISTANT = "Waiting for the assistant to finish…";

/** A full turn -- reading the files, proposing, then writing -- is slow. */
export const TURN_TIMEOUT = 180_000;

/**
 * Asks for an exact, checkable edit, then for a long answer after it: the
 * proposal can only be resolved once the turn ends, and that tail of writing
 * keeps the turn open long enough to see Save and Dismiss refused meanwhile.
 */
export function proposeThenExplainPrompt(
  change: string,
  proposalTool: string,
): string {
  return [
    `${change} and change nothing else.`,
    `Propose the change with ${proposalTool} first.`,
    "Only after proposing it, explain the change in a detailed answer of at least 200 words.",
  ].join(" ");
}

type AssistantPanelLabels = {
  /** The proposal banner's heading. */
  proposal: string;
  /** The placeholder of the banner's message field. */
  messagePlaceholder: string;
};

/**
 * The AI assistant beside a code editor. Web apps and pipelines share the chat
 * panel and the proposal banner; only their labels and how a save shows differ.
 */
export abstract class AssistantPanel {
  constructor(
    protected readonly page: Page,
    private readonly labels: AssistantPanelLabels,
  ) {}

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
    return this.page.getByText(this.labels.proposal);
  }

  get dismissButton(): Locator {
    return this.page.getByRole("button", { name: "Dismiss" });
  }

  get proposalMessageInput(): Locator {
    return this.page.getByPlaceholder(this.labels.messagePlaceholder);
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

  /** Saves the proposal under `message`, which commits and publishes it. */
  async accept(message: string) {
    await this.proposalMessageInput.fill(message);
    await this.saveButton.click();
    await this.expectSaved();
    await expect(this.proposalBanner).toBeHidden();
  }

  protected abstract expectSaved(): Promise<void>;
}
