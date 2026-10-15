import { Locator, Page, expect } from "@playwright/test";

import { McpPermissionMatrix } from "./McpPermissionMatrix";

/**
 * /mcp/authorize: the consent screen an MCP client's authorization request
 * lands on, and the page the backend shows once it is granted.
 */
export class McpAuthorizePage {
  readonly matrix: McpPermissionMatrix;

  constructor(private readonly page: Page) {
    this.matrix = new McpPermissionMatrix(page.locator("body"));
  }

  heading(clientName: string): Locator {
    return this.page.getByRole("heading", {
      name: `Authorize ${clientName}`,
      level: 1,
    });
  }

  get authorizeButton(): Locator {
    return this.page.getByRole("button", { name: "Authorize", exact: true });
  }

  get successHeading(): Locator {
    return this.page.getByRole("heading", { name: "Authorization successful" });
  }

  connectedText(clientName: string): Locator {
    return this.page.locator("p", { hasText: `${clientName} is connected.` });
  }

  /** Opens the request; a signed-in user is sent on to the consent screen. */
  async open(authorizeUrl: string) {
    await this.page.goto(authorizeUrl);
    await this.page.waitForURL(/\/mcp\/authorize\//);
  }

  /**
   * Consents, and returns the authorization code. The success page sends it to
   * the client's redirect URI, which nothing serves: the request is answered
   * here, and the page only shows its confirmation once it is.
   */
  async authorize(redirectUri: string): Promise<string> {
    const codes: string[] = [];
    await this.page.route(
      (url) => url.href.startsWith(redirectUri),
      async (route) => {
        const code = new URL(route.request().url()).searchParams.get("code");
        if (code) {
          codes.push(code);
        }
        await route.fulfill({ status: 200, body: "" });
      },
    );
    await this.authorizeButton.click();
    await expect(this.successHeading).toBeVisible();
    expect(codes, "no authorization code reached the redirect URI").toHaveLength(1);
    return codes[0];
  }
}
