import { Locator, Page } from "@playwright/test";

export type OrganizationSection =
  | "Workspaces"
  | "Members"
  | "External Collaborators"
  | "Datasets"
  | "Settings";

/**
 * The left-hand navigation rendered by OrganizationLayout on every page of the
 * organization section.
 */
export class OrganizationSidebar {
  constructor(private readonly page: Page) {}

  get nav(): Locator {
    return this.page.getByRole("navigation");
  }

  /** The account button at the foot of the sidebar, labelled with the email. */
  get userMenuButton(): Locator {
    return this.page.getByRole("button", { name: /@/ });
  }

  link(section: OrganizationSection): Locator {
    return this.nav.getByRole("link", { name: section, exact: true });
  }

  /** Back-link to the organization picker, labelled with the short name. */
  organizationLink(label: string): Locator {
    return this.page.getByRole("link", { name: label, exact: true });
  }

  async open(section: OrganizationSection) {
    await this.link(section).click();
  }
}
