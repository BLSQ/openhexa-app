import { expect, test } from "../fixtures/cleanup";
import { WorkspaceNotebooksPage } from "../pages/WorkspaceNotebooksPage";

test.describe("Workspace notebooks", () => {
  test("JupyterHub starts a server and opens JupyterLab", async ({ page }) => {
    // A cold start provisions a server, which can take a few minutes.
    test.setTimeout(360_000);
    const notebooks = new WorkspaceNotebooksPage(page);

    await notebooks.goto();
    await expect(notebooks.serverFrame).toHaveAttribute(
      "src",
      /\/user\/[^/]+\/[^/]+\/?$/,
      { timeout: 300_000 },
    );

    await expect
      .poll(async () => (await notebooks.labFrame()?.title()) ?? "", {
        timeout: 300_000,
        intervals: [2_000],
      })
      .toBe("JupyterLab");
  });
});
