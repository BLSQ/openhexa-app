import { Locator, Page } from "@playwright/test";

/** /mcp: the tools the OpenHEXA MCP server exposes, and its setup guide. */
export class McpPage {
  constructor(private readonly page: Page) {}

  get heading(): Locator {
    return this.page.getByRole("heading", { name: "MCP Tools", level: 1 });
  }

  /** "<server> v<version> · Protocol <date> · <n> tools" */
  get summary(): Locator {
    return this.page.getByText(/ · Protocol .+ · \d+ tools?$/);
  }

  /** A tool's card, by its name. */
  tool(name: string): Locator {
    return this.page.getByText(name, { exact: true });
  }

  get parameterHeadings(): Locator {
    return this.page.getByText("Parameters", { exact: true });
  }

  get installLink(): Locator {
    return this.page.getByRole("link", { name: "Install" });
  }

  get guideHeading(): Locator {
    return this.page.getByRole("heading", {
      name: "MCP Setup Guide",
      level: 1,
    });
  }

  get backToToolsLink(): Locator {
    return this.page.getByRole("link", { name: "← Back to MCP Tools" });
  }
}
