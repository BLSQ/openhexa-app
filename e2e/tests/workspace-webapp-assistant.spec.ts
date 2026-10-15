import { expect, test } from "../fixtures/cleanup";
import { uniqueName } from "../helpers/confirm";
import { ServedWebapp } from "../pages/ServedWebapp";
import { proposeThenExplainPrompt } from "../pages/AssistantPanel";
import {
  CreateWebappWithAIDialog,
  WebappAssistantPanel,
  createWebappPrompt,
  headingChangePrompt,
} from "../pages/WebappAssistantPanel";
import { WorkspaceDataStudioPage } from "../pages/WorkspaceDataStudioPage";
import { WorkspaceWebappsPage } from "../pages/WorkspaceWebappsPage";

/** What a new static app is created with, from the default template. */
const TEMPLATE_HEADING = "Hello World";

/** The regions of Senegal, loaded into the test workspace's database. */
const REGIONS_SQL = "SELECT code, name FROM level_2_region ORDER BY code";

// These talk to the real agent on the target environment, so each turn takes
// as long as the model does.
test.describe.configure({ timeout: 420_000 });

test.describe("Web app AI assistant", () => {
  test("a web app created with AI opens in the editor, reading a saved query", async ({
    page,
    cleanup,
  }) => {
    const webapps = new WorkspaceWebappsPage(page);
    const studio = new WorkspaceDataStudioPage(page);
    const dialog = new CreateWebappWithAIDialog(page);
    const assistant = new WebappAssistantPanel(page);
    const served = new ServedWebapp(await page.context().newPage());
    const name = uniqueName("e2e-ai-webapp");
    const heading = uniqueName("E2E-AI-WEBAPP");

    // Shared with the workspace: an app runs as a service account of the
    // workspace, which cannot see private queries.
    const query = await studio.createWithApi(REGIONS_SQL, {
      name: uniqueName("e2e regions"),
      description: "Regions of Senegal, for a web app created with AI.",
      visibility: "WORKSPACE",
    });
    cleanup.add(`saved query ${query.slug}`, () =>
      studio.deleteWithApi(query.id),
    );
    const prompt = createWebappPrompt(name, heading, query.slug);

    // Registered before the agent runs: if the test dies while it is still
    // working, the dialog holds the page with a beforeunload prompt that
    // cleanup has to get past.
    cleanup.add(`web app ${name}`, async () => {
      page.on("dialog", (d) => d.accept());
      await webapps.deleteIfPresent(name);
    });

    await webapps.goto();
    await dialog.open();
    await dialog.submit(prompt);

    await test.step("the dialog shows the agent at work", async () => {
      await expect(dialog.step("Generating web app code")).toBeVisible();
      await expect(dialog.submitButton).toBeDisabled();
    });

    const slug = await test.step("it opens the new app's code", async () => {
      const slug = await dialog.waitForWebapp();
      if (slug !== name) {
        cleanup.add(`web app ${slug}`, () => webapps.deleteIfPresent(slug));
      }
      expect(slug, "the agent did not use the requested name").toBe(name);

      await expect(webapps.treeFile("index.html")).toBeVisible();
      await expect(webapps.codeEditor).toContainText(heading);
      expect(await webapps.readFile(slug, "index.html")).toContain(query.slug);
      return slug;
    });

    await test.step("the conversation moves to the app", async () => {
      await expect(assistant.heading).toBeVisible();
      await expect(assistant.message(prompt)).toBeVisible();

      await webapps.gotoTab(slug, "Code");
      await expect(assistant.heading).toBeVisible();
      await expect(assistant.message(prompt)).toBeVisible();
      await expect(assistant.proposalBanner).toBeHidden();
    });

    await test.step("it was given access to the database", async () => {
      await webapps.gotoTab(slug, "API access");
      await expect(webapps.apiScope("Read database")).toBeChecked();
    });

    await test.step("it is served, with the query's rows", async () => {
      await served.goto(await webapps.servedUrl(slug));
      await expect(served.heading(heading)).toBeVisible();
      await expect(served.text("Dakar")).toBeVisible({ timeout: 30_000 });
    });

    await test.step("it is listed with the workspace's apps", async () => {
      await webapps.expectVisible(name);
    });
  });

  test("a dismissed proposal leaves the app as it was", async ({
    page,
    cleanup,
  }) => {
    const webapps = new WorkspaceWebappsPage(page);
    const assistant = new WebappAssistantPanel(page);
    const heading = uniqueName("E2E-REJECTED");

    const slug = await webapps.create("Static", uniqueName("e2e assistant"));
    cleanup.add(`web app ${slug}`, () => webapps.deleteIfPresent(slug));

    await webapps.gotoTab(slug, "Code");
    await expect(webapps.codeEditor).toContainText(TEMPLATE_HEADING);
    await assistant.open();
    await assistant.send(headingChangePrompt(heading));

    await test.step("the proposal waits for the agent to finish", async () => {
      await assistant.waitForProposal();
      await expect(webapps.codeEditor).toContainText(heading);
    });

    await test.step("dismissing it restores the saved code", async () => {
      await assistant.dismiss();
      await expect(webapps.codeEditor).not.toContainText(heading);
      await expect(webapps.codeEditor).toContainText(TEMPLATE_HEADING);
    });

    await test.step("and nothing was committed", async () => {
      await webapps.gotoTab(slug, "History");
      await expect(webapps.commitLink("Initial content")).toBeVisible();
      await expect(webapps.commitTitle("Initial content")).toContainText(
        "Published",
      );
    });

    await test.step("it stays dismissed after a reload", async () => {
      await webapps.gotoTab(slug, "Code");
      await expect(webapps.codeEditor).toContainText(TEMPLATE_HEADING);
      await expect(assistant.proposalBanner).toBeHidden();
    });
  });

  test("a saved proposal is committed and served", async ({
    page,
    cleanup,
  }) => {
    const webapps = new WorkspaceWebappsPage(page);
    const assistant = new WebappAssistantPanel(page);
    const served = new ServedWebapp(await page.context().newPage());
    const heading = uniqueName("E2E-ACCEPTED");
    const commitMessage = uniqueName("e2e: accept the assistant's proposal");

    const slug = await webapps.create("Static", uniqueName("e2e assistant"));
    cleanup.add(`web app ${slug}`, () => webapps.deleteIfPresent(slug));

    await webapps.gotoTab(slug, "Code");
    await expect(webapps.codeEditor).toContainText(TEMPLATE_HEADING);
    await assistant.open();
    await assistant.send(headingChangePrompt(heading));

    await test.step("the proposal waits for the agent to finish", async () => {
      await assistant.waitForProposal();
      await expect(webapps.codeEditor).toContainText(heading);
    });

    await test.step("saving it commits under the edited message", async () => {
      await assistant.accept(commitMessage);

      await webapps.gotoTab(slug, "History");
      await expect(webapps.commitTitle(commitMessage)).toContainText(
        "Published",
      );
    });

    await test.step("the served app shows the change", async () => {
      await served.goto(await webapps.servedUrl(slug));
      await expect(served.heading(heading)).toBeVisible();
    });

    await test.step("the conversation is kept with the app", async () => {
      await webapps.gotoTab(slug, "Code");
      await expect(assistant.heading).toBeVisible();
      await expect(
        assistant.message(headingChangePrompt(heading)),
      ).toBeVisible();
      await expect(assistant.proposalBanner).toBeHidden();
    });
  });

  test("a second request adds to the pending proposal; a file is deleted", async ({
    page,
    cleanup,
  }) => {
    test.setTimeout(600_000);
    const webapps = new WorkspaceWebappsPage(page);
    const assistant = new WebappAssistantPanel(page);
    const served = new ServedWebapp(await page.context().newPage());
    const heading = uniqueName("E2E-CHAINED");
    const note = uniqueName("e2e-note");

    const slug = await webapps.create("Static", uniqueName("e2e assistant"));
    cleanup.add(`web app ${slug}`, () => webapps.deleteIfPresent(slug));

    await webapps.gotoTab(slug, "Code");
    await assistant.open();

    await test.step("two requests make one proposal", async () => {
      await assistant.send(headingChangePrompt(heading));
      await assistant.waitForProposal();

      await assistant.send(
        proposeThenExplainPrompt(
          `Add a file named notes.txt whose only content is the line "${note}"`,
          "propose_webapp_version",
        ),
      );
      await assistant.waitForNextProposal();
      await expect(webapps.treeFile("notes.txt")).toBeVisible();
      await expect(webapps.codeEditor).toContainText(heading);
    });

    await test.step("saving it publishes both changes", async () => {
      await assistant.accept(uniqueName("e2e: heading and notes"));
      const url = await webapps.servedUrl(slug);
      await served.goto(url);
      await expect(served.heading(heading)).toBeVisible();
      await served.goto(`${url.replace(/\/$/, "")}/notes.txt`);
      await expect(served.text(note)).toBeVisible();
    });

    await test.step("a proposal can delete a file", async () => {
      await webapps.gotoTab(slug, "Code");
      await assistant.send(
        proposeThenExplainPrompt("Delete the file notes.txt", "propose_webapp_version"),
      );
      await assistant.waitForProposal();
      await webapps.treeFile("notes.txt").click();
      await expect(page.getByText("This file will be deleted")).toBeVisible();

      await assistant.accept(uniqueName("e2e: drop the notes"));
      await webapps.gotoTab(slug, "Code");
      await expect(webapps.treeFile("notes.txt")).toHaveCount(0);
    });
  });
});
