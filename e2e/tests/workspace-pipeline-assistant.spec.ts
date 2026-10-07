import { expect, test } from "../fixtures/cleanup";
import { uniqueName } from "../helpers/confirm";
import {
  ASSISTANT_PIPELINE_SOURCE,
  CreatePipelineWithAIDialog,
  ORIGINAL_LOG_MESSAGE,
  PipelineAssistantPanel,
  createPipelinePrompt,
  logMessageChangePrompt,
} from "../pages/PipelineAssistantPanel";
import { WorkspacePipelinesPage } from "../pages/WorkspacePipelinesPage";

// These talk to the real agent on the target environment, so each turn takes
// as long as the model does.
test.describe.configure({ timeout: 420_000 });

test.describe("Pipeline AI assistant", () => {
  test("a pipeline created with AI opens in the editor with its conversation", async ({
    page,
    cleanup,
  }) => {
    const pipelines = new WorkspacePipelinesPage(page);
    const dialog = new CreatePipelineWithAIDialog(page);
    const assistant = new PipelineAssistantPanel(page);
    const name = uniqueName("e2e-ai-pipeline");
    const message = uniqueName("E2E-CREATED");
    const prompt = createPipelinePrompt(name, message);

    // Registered before the agent runs: if the test dies while it is still
    // working, the dialog holds the page with a beforeunload prompt that
    // cleanup has to get past.
    cleanup.add(`pipeline ${name}`, async () => {
      page.on("dialog", (d) => d.accept());
      await pipelines.deleteIfPresent(name);
    });

    await pipelines.goto();
    await dialog.open();
    await dialog.submit(prompt);

    await test.step("the dialog shows the agent at work", async () => {
      await expect(dialog.step("Generating pipeline code")).toBeVisible();
      await expect(dialog.submitButton).toBeDisabled();
    });

    const code = await test.step("it opens the new pipeline's code", async () => {
      const code = await dialog.waitForPipeline();
      if (code !== name) {
        cleanup.add(`pipeline ${code}`, () => pipelines.deleteIfPresent(code));
      }
      expect(code, "the agent did not use the requested name").toBe(name);

      await expect(page.getByRole("heading", { name, level: 2 })).toBeVisible();
      await expect(pipelines.filesHeading("v1")).toBeVisible();
      await expect(pipelines.codeEditor).toContainText(message);
      return code;
    });

    await test.step("the conversation moves to the pipeline", async () => {
      await expect(assistant.heading).toBeVisible();
      await expect(assistant.message(prompt)).toBeVisible();

      await pipelines.gotoCode(code);
      await expect(assistant.heading).toBeVisible();
      await expect(assistant.message(prompt)).toBeVisible();
      await expect(assistant.proposalBanner).toBeHidden();
    });

    await test.step("it is listed with the workspace's pipelines", async () => {
      await pipelines.goto();
      await expect(pipelines.row(name)).toBeVisible();
    });
  });

  test("a dismissed proposal leaves the pipeline as it was", async ({
    page,
    cleanup,
  }) => {
    const pipelines = new WorkspacePipelinesPage(page);
    const assistant = new PipelineAssistantPanel(page);
    const message = uniqueName("E2E-REJECTED");

    const code = await pipelines.createWithSource(
      uniqueName("e2e-assistant"),
      ASSISTANT_PIPELINE_SOURCE,
    );
    cleanup.add(`pipeline ${code}`, () => pipelines.deleteIfPresent(code));

    await pipelines.gotoCode(code);
    await expect(pipelines.codeEditor).toContainText(ORIGINAL_LOG_MESSAGE);
    await assistant.open();
    await assistant.send(logMessageChangePrompt(message));

    await test.step("the proposal waits for the agent to finish", async () => {
      await assistant.waitForProposal();
      await expect(pipelines.codeEditor).toContainText(message);
    });

    await test.step("dismissing it restores the saved code", async () => {
      await assistant.dismiss();
      await expect(pipelines.codeEditor).not.toContainText(message);
      await expect(pipelines.codeEditor).toContainText(ORIGINAL_LOG_MESSAGE);
      await expect(assistant.saveButton).toBeHidden();
    });

    await test.step("and no version was published", async () => {
      await pipelines.gotoVersions(code);
      await expect(pipelines.versionHeading("v1")).toBeVisible();
      await expect(pipelines.versionHeading("v2")).toHaveCount(0);
    });

    await test.step("it stays dismissed after a reload", async () => {
      await pipelines.gotoCode(code);
      await expect(pipelines.codeEditor).toContainText(ORIGINAL_LOG_MESSAGE);
      await expect(assistant.proposalBanner).toBeHidden();
    });
  });

  test("a saved proposal is published as a new version", async ({
    page,
    cleanup,
  }) => {
    const pipelines = new WorkspacePipelinesPage(page);
    const assistant = new PipelineAssistantPanel(page);
    const message = uniqueName("E2E-ACCEPTED");
    const description = uniqueName("e2e: accept the assistant's proposal");

    const code = await pipelines.createWithSource(
      uniqueName("e2e-assistant"),
      ASSISTANT_PIPELINE_SOURCE,
    );
    cleanup.add(`pipeline ${code}`, () => pipelines.deleteIfPresent(code));

    await pipelines.gotoCode(code);
    await expect(pipelines.codeEditor).toContainText(ORIGINAL_LOG_MESSAGE);
    await assistant.open();
    await assistant.send(logMessageChangePrompt(message));

    await test.step("the proposal waits for the agent to finish", async () => {
      await assistant.waitForProposal();
      await expect(pipelines.codeEditor).toContainText(message);
    });

    await test.step("saving it publishes v2 with the edited description", async () => {
      await assistant.accept(description);
      await expect(pipelines.filesHeading("v2")).toBeVisible();
      await expect(pipelines.codeEditor).toContainText(message);

      await pipelines.gotoVersions(code);
      await expect(pipelines.versionHeading("v2")).toBeVisible();
      await expect(page.getByText(description, { exact: true })).toBeVisible();
    });

    await test.step("the conversation is kept with the pipeline", async () => {
      await pipelines.gotoCode(code);
      await expect(pipelines.filesHeading("v2")).toBeVisible();
      await expect(pipelines.codeEditor).toContainText(message);
      await expect(assistant.heading).toBeVisible();
      await expect(
        assistant.message(logMessageChangePrompt(message)),
      ).toBeVisible();
      await expect(assistant.proposalBanner).toBeHidden();
    });
  });
});
