import { Locator, expect } from "@playwright/test";

export type McpLevel = "Read & Write" | "Read" | "No access";

/** "all" for the row that sets every resource at once, else a resource. */
export type McpGroup =
  | "all"
  | "WORKSPACES"
  | "FILES"
  | "DATASETS"
  | "PIPELINES"
  | "TEMPLATES"
  | "WEBAPPS"
  | "DATABASES"
  | "SAVED_QUERIES"
  | "CONNECTIONS";

/**
 * The permission editor an MCP connection is granted with, on the consent
 * screen and again on the account page: the workspaces it reaches, and an
 * access level per resource.
 */
export class McpPermissionMatrix {
  constructor(private readonly root: Locator) {}

  workspaceCheckbox(slug: string): Locator {
    return this.root.locator(`input[type="checkbox"][id$="-workspace-${slug}"]`);
  }

  get deselectAllWorkspaces(): Locator {
    return this.root.getByRole("button", { name: "Deselect all" });
  }

  /**
   * The level radios are visually hidden; their labels take the click. The
   * inner locator is resolved from the label, so it is built from the page.
   */
  levelLabel(group: McpGroup, level: McpLevel): Locator {
    return this.root
      .locator("label")
      .filter({
        has: this.root
          .page()
          .locator(`input[type="radio"][name$="-level-${group}"]`),
      })
      .filter({ hasText: new RegExp(`^${level}$`) });
  }

  levelRadio(group: McpGroup, level: McpLevel): Locator {
    return this.levelLabel(group, level).locator("input");
  }

  async setLevel(group: McpGroup, level: McpLevel) {
    await this.levelLabel(group, level).click();
    await expect(this.levelRadio(group, level)).toBeChecked();
  }
}
