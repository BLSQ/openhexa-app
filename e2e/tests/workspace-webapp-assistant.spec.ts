import { expect, test } from "../fixtures/cleanup";
import { uniqueName } from "../helpers/confirm";
import { ServedWebapp } from "../pages/ServedWebapp";
import {
  WebappAssistantPanel,
  headingChangePrompt,
} from "../pages/WebappAssistantPanel";
import { WorkspaceWebappsPage } from "../pages/WorkspaceWebappsPage";

/** What a new static app is created with, from the default template. */
const TEMPLATE_HEADING = "Hello World";

// These talk to the real agent on the target environment, so each turn takes
// as long as the model does.
test.describe.configure({ timeout: 420_000 });

test.describe("Web app AI assistant", () => {
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
});
