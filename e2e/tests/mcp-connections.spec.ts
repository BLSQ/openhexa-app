import { mergeTests } from "@playwright/test";
import { randomUUID } from "node:crypto";

import { workspace } from "../config/environment";
import { test as cleanupTest } from "../fixtures/cleanup";
import { expect, test as disposableTest } from "../fixtures/disposableWorkspace";
import { uniqueName } from "../helpers/confirm";
import { MCP_REDIRECT_URI, McpClient } from "../helpers/mcpClient";
import { AccountSettingsPage } from "../pages/AccountSettingsPage";
import { McpAuthorizePage } from "../pages/McpAuthorizePage";

const test = mergeTests(cleanupTest, disposableTest);

test.describe("MCP connections", () => {
  test("a client is granted chosen tools and one workspace, widened, then revoked", async ({
    page,
    cleanup,
    disposableWorkspace,
  }) => {
    // Provisioning a workspace the grant leaves out.
    test.setTimeout(300_000);
    const account = new AccountSettingsPage(page);
    const consent = new McpAuthorizePage(page);
    const client = await McpClient.register(uniqueName("e2e MCP client"));
    cleanup.add("the MCP client's requests", () => client.dispose());
    cleanup.add(`MCP connection ${client.name}`, () =>
      account.revokeMcpConnectionIfPresent(client.name),
    );
    const otherSlug = await disposableWorkspace.create();

    await test.step("the consent screen starts read-only, on every workspace", async () => {
      await consent.open(client.authorizeUrl);
      await expect(consent.heading(client.name)).toBeVisible();
      await expect(consent.matrix.levelRadio("all", "Read")).toBeChecked();
      await expect(
        consent.matrix.workspaceCheckbox(workspace.slug),
      ).toBeChecked();
      await expect(consent.matrix.workspaceCheckbox(otherSlug)).toBeChecked();
    });

    await test.step("only the test workspace, with reading workspaces and pipelines, is granted", async () => {
      await consent.matrix.deselectAllWorkspaces.click();
      await consent.matrix.workspaceCheckbox(workspace.slug).check();
      await consent.matrix.setLevel("all", "No access");
      await consent.matrix.setLevel("WORKSPACES", "Read");
      await consent.matrix.setLevel("PIPELINES", "Read");
      await expect(
        consent.matrix.levelRadio("DATASETS", "No access"),
      ).toBeChecked();
    });

    const token = await test.step("authorizing hands the client a token", async () => {
      const code = await consent.authorize(MCP_REDIRECT_URI);
      await expect(consent.connectedText(client.name)).toBeVisible();
      return client.exchangeCode(code);
    });

    await test.step("the client sees the granted tools, and only those", async () => {
      const tools = await client.listTools(token);
      expect(tools).toContain("list_workspaces");
      expect(tools).toContain("list_pipelines");
      expect(tools).toContain("get_pipeline");
      expect(tools).not.toContain("run_pipeline");
      expect(tools).not.toContain("list_datasets");
      // The documentation needs no grant.
      expect(tools).toContain("get_help_or_doc");

      const refusal = await client.callTool(token, "list_datasets", {
        workspace_slug: workspace.slug,
      });
      expect(refusal).toContain(client.name);
      const pipelines = await client.callTool(token, "list_pipelines", {
        workspace_slug: workspace.slug,
      });
      expect(pipelines, pipelines).not.toContain(client.name);
      expect(() => JSON.parse(pipelines)).not.toThrow();
    });

    await test.step("a write is refused, not just hidden", async () => {
      const refusal = await client.callTool(token, "run_pipeline", {
        pipeline_id: randomUUID(),
      });
      expect(refusal).toContain(client.name);
    });

    await test.step("the token is blind to the workspace left out of the grant", async () => {
      // The account can see both: it has just created the other one.
      const workspaces = JSON.parse(
        await client.callTool(token, "list_workspaces", { per_page: 100 }),
      );
      const slugs = workspaces.workspaces.items.map(
        (item: { slug: string }) => item.slug,
      );
      expect(slugs).toContain(workspace.slug);
      expect(slugs).not.toContain(otherSlug);

      const pipelines = JSON.parse(
        await client.callTool(token, "list_pipelines", {
          workspace_slug: otherSlug,
        }),
      );
      expect(pipelines.pipelines.totalItems).toBe(0);
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
      await expect(matrix.workspaceCheckbox(otherSlug)).not.toBeChecked();

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

    await test.step("the write now gets through, but not into the other workspace", async () => {
      // A pipeline that does not exist: the call is let in, then fails on
      // its own terms, without running anything.
      const run = await client.callTool(token, "run_pipeline", {
        pipeline_id: randomUUID(),
      });
      expect(run).not.toContain(client.name);
      expect(run).toContain("PIPELINE_NOT_FOUND");

      const created = JSON.parse(
        await client.callTool(token, "create_pipeline", {
          workspace_slug: otherSlug,
          name: uniqueName("e2e-mcp-sneaky"),
          files_json: JSON.stringify([
            { path: "pipeline.py", content: "from openhexa.sdk import pipeline\n" },
          ]),
        }),
      );
      expect(created.success).toBe(false);
      expect(created.errors).toContain("WORKSPACE_NOT_FOUND");
    });

    await test.step("revoking it cuts the client off at once", async () => {
      await account.revokeMcpConnection(client.name);
      // A call in the same instant can still get through; the next is refused.
      await expect.poll(() => client.statusOf(token), { timeout: 10_000 }).toBe(401);
    });
  });
});
