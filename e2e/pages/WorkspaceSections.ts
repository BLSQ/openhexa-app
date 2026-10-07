import { Locator, Page, expect } from "@playwright/test";

/**
 * A workspace's sections, and the button on each that only someone allowed
 * to add to it is shown. The pages are rendered on the server with the
 * viewer's permissions, so once the breadcrumb is there, so is the button
 * -- or it never will be.
 */
export const SECTIONS = {
  Pipelines: { path: "pipelines/", create: "Create" },
  Files: { path: "files/", create: "Upload files" },
  Datasets: { path: "datasets/", create: "Create" },
  Connections: { path: "connections/", create: "Add connection" },
  "Web Apps": { path: "webapps/", create: "Create" },
} as const;

export type Section = keyof typeof SECTIONS;

/** The workspace sidebar and section headers, as a given account sees them. */
export class WorkspaceSections {
  constructor(
    private readonly page: Page,
    private readonly workspaceSlug: string,
  ) {}

  get sidebar(): Locator {
    return this.page.getByRole("navigation").first();
  }

  sidebarLink(label: string): Locator {
    return this.sidebar.getByRole("link", { name: label, exact: true });
  }

  breadcrumb(section: Section): Locator {
    return this.page
      .getByRole("navigation", { name: "Breadcrumbs" })
      .getByRole("link", { name: section, exact: true });
  }

  createButton(section: Section): Locator {
    return this.page
      .getByRole("banner")
      .getByRole("button", { name: SECTIONS[section].create, exact: true });
  }

  async goto(section: Section) {
    await this.page.goto(
      `/workspaces/${this.workspaceSlug}/${SECTIONS[section].path}`,
    );
    await expect(this.breadcrumb(section)).toBeVisible();
  }

  /** Files has its actions in the page, not in the header. */
  private sectionCreateButton(section: Section): Locator {
    return section === "Files"
      ? this.page
          .getByRole("main")
          .getByRole("button", { name: SECTIONS.Files.create })
      : this.createButton(section);
  }

  async expectCanCreate(section: Section, can: boolean) {
    await this.goto(section);
    const button = this.sectionCreateButton(section);
    if (can) {
      await expect(button, `${section} offers to create`).toBeVisible();
    } else {
      await expect(button, `${section} offers to create`).toHaveCount(0);
    }
  }
}
