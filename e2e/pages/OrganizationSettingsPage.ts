import { Locator, Page } from "@playwright/test";

import { organizationPaths } from "../config/environment";
import { OrganizationSidebar } from "./OrganizationSidebar";

export class OrganizationSettingsPage {
  constructor(private readonly page: Page) {}

  get sidebar() {
    return new OrganizationSidebar(this.page);
  }

  get heading(): Locator {
    return this.page.getByRole("heading", {
      name: "Organization Settings",
      level: 1,
    });
  }

  async goto() {
    await this.page.goto(organizationPaths.settings);
  }

  /**
   * The settings cards carry no test ids, so a card is addressed as the
   * innermost element containing both its heading and a piece of text unique to
   * it. Ancestors always precede descendants in document order, so the last
   * match is the deepest one -- the card itself rather than a page wrapper.
   */
  private card(heading: string, anchorText: string): Locator {
    return this.page
      .locator("div, article")
      .filter({
        has: this.page.getByRole("heading", { name: heading, exact: true }),
      })
      .filter({ hasText: anchorText })
      .last();
  }

  get generalCard(): Locator {
    return this.card("General", "Organization Name");
  }

  get aiAssistantCard(): Locator {
    return this.card("AI Assistant", "Provider");
  }

  get usageAndLimitsCard(): Locator {
    return this.card("Usage & Limits", "Workspaces");
  }

  get editGeneralButton(): Locator {
    return this.generalCard.getByRole("button", { name: "Edit" });
  }

  /** Read-mode value of a `<dt>`/`<dd>` pair in the General card. */
  generalValue(term: string): Locator {
    return this.generalCard
      .getByRole("term")
      .filter({ hasText: term })
      .locator("xpath=following-sibling::dd");
  }

  get nameInput(): Locator {
    return this.generalCard.getByPlaceholder("Enter organization name");
  }

  get shortNameInput(): Locator {
    return this.generalCard.getByPlaceholder("Enter short name");
  }

  get saveChangesButton(): Locator {
    return this.generalCard.getByRole("button", { name: "Save Changes" });
  }

  get cancelButton(): Locator {
    return this.generalCard.getByRole("button", { name: "Cancel" });
  }

  /** A single figure in the Usage & Limits card, e.g. "Users" or "Workspaces". */
  usageMetric(label: string): Locator {
    return this.usageAndLimitsCard
      .getByText(label, { exact: true })
      .locator("xpath=following-sibling::p");
  }

  get manageSubscriptionLink(): Locator {
    return this.usageAndLimitsCard.getByRole("link", {
      name: "Manage subscription",
    });
  }
}
