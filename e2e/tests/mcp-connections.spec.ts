import { workspace } from "../config/environment";
import { expect, test } from "../fixtures/cleanup";
import { uniqueName } from "../helpers/confirm";
import { MCP_REDIRECT_URI, McpClient } from "../helpers/mcpClient";
import { AccountSettingsPage } from "../pages/AccountSettingsPage";
import { McpAuthorizePage } from "../pages/McpAuthorizePage";

test.describe("MCP connections", () => {
  test("a client is granted chosen tools, which are widened and then revoked", async ({
    page,
    cleanup,
  }) => {
    test.setTimeout(180_000);
    const account = new AccountSettingsPage(page);
    const consent = new McpAuthorizePage(page);
    const client = await McpClient.register(uniqueName("e2e MCP client"));
    cleanup.add("the MCP client's requests", () => client.dispose());
    cleanup.add(`MCP connection ${client.name}`, () =>
      account.revokeMcpConnectionIfPresent(client.name),
    );

    await test.step("the consent screen starts read-only, on every workspace", async () => {
      await consent.open(client.authorizeUrl);
      await expect(consent.heading(client.name)).toBeVisible();
      await expect(consent.matrix.levelRadio("all", "Read")).toBeChecked();
      await expect(
        consent.matrix.workspaceCheckbox(workspace.slug),
      ).toBeChecked();
    });

    await test.step("only the test workspace and reading pipelines are granted", async () => {
      await consent.matrix.deselectAllWorkspaces.click();
      await consent.matrix.workspaceCheckbox(workspace.slug).check();
      await consent.matrix.setLevel("all", "No access");
      await consent.matrix.setLevel("PIPELINES", "Read");
      await expect(
        consent.matrix.levelRadio("WORKSPACES", "No access"),
      ).toBeChecked();
    });

    const token = await test.step("authorizing hands the client a token", async () => {
      const code = await consent.authorize(MCP_REDIRECT_URI);
      await expect(consent.connectedText(client.name)).toBeVisible();
      return client.exchangeCode(code);
    });

    await test.step("the client sees the granted tools, and only those", async () => {
      const tools = await client.listTools(token);
      expect(tools).toContain("list_pipelines");
      expect(tools).toContain("get_pipeline");
      expect(tools).not.toContain("run_pipeline");
      expect(tools).not.toContain("list_workspaces");
      // The documentation needs no grant.
      expect(tools).toContain("get_help_or_doc");

      const refusal = await client.callTool(token, "list_workspaces");
      expect(refusal).toContain(client.name);
      const pipelines = await client.callTool(token, "list_pipelines", {
        workspace_slug: workspace.slug,
      });
      expect(pipelines, pipelines).not.toContain(client.name);
      expect(() => JSON.parse(pipelines)).not.toThrow();
    });

    await test.step("the account page lists it, and widens it to writing pipelines", async () => {
      await account.goto();
      await expect(account.mcpConnectionSummary(client.name)).toHaveText(
        /^\d+ of \d+ tools · 1 workspaces?$/,
      );
      await account.expandMcpConnection(client.name);
      const matrix = account.mcpMatrix(client.name);
      await expect(matrix.levelRadio("PIPELINES", "Read")).toBeChecked();
      await expect(matrix.workspaceCheckbox(workspace.slug)).toBeChecked();

      await matrix.setLevel("PIPELINES", "Read & Write");
      await expect(account.mcpUnsavedBadge(client.name)).toBeVisible();
      await account.mcpSaveButton(client.name).click();
      await expect(account.mcpUnsavedBadge(client.name)).toBeHidden();

      await account.goto();
      await account.expandMcpConnection(client.name);
      await expect(
        account.mcpMatrix(client.name).levelRadio("PIPELINES", "Read & Write"),
      ).toBeChecked();
      expect(await client.listTools(token)).toContain("run_pipeline");
    });

    await test.step("revoking it cuts the client off at once", async () => {
      await account.revokeMcpConnection(client.name);
      // A call in the same instant can still get through; the next is refused.
      await expect.poll(() => client.statusOf(token), { timeout: 10_000 }).toBe(401);
    });
  });
});
