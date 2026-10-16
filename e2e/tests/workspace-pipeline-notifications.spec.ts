import { mergeTests } from "@playwright/test";

import { mailgun, workspacePaths } from "../config/environment";
import { test as cleanupTest } from "../fixtures/cleanup";
import { expect, test as mailboxTest } from "../fixtures/mailbox";
import { uniqueName } from "../helpers/confirm";
import { linkTo } from "../helpers/mailbox";
import { PipelineDetailPage } from "../pages/PipelineDetailPage";
import {
  RUN_PIPELINE_SOURCE,
  WorkspacePipelinesPage,
} from "../pages/WorkspacePipelinesPage";

const test = mergeTests(cleanupTest, mailboxTest);

/**
 * Run reports go to a permanent account on the mailbox domain, a member of
 * the test workspace that the suite never signs in as. The reports are sent
 * by the pipelines runner once a run ends, after the run's page already
 * shows its verdict.
 */
test.describe("Pipeline run notifications", () => {
  test.skip(
    !mailgun,
    "Needs E2E_MAILGUN_API_KEY for a mailbox the suite can read",
  );
  // Three pipeline containers are provisioned and run, one after the other.
  test.describe.configure({ timeout: 900_000 });

  test("recipients get a run report by email, Error-level ones only for failures", async ({
    page,
    cleanup,
    mailbox,
  }) => {
    const { reportRecipient: recipient, reportRecipientName } = mailgun!;
    const pipelines = new WorkspacePipelinesPage(page);
    const code = await pipelines.createWithSource(
      uniqueName("e2e-report"),
      RUN_PIPELINE_SOURCE,
    );
    cleanup.add(`pipeline ${code}`, () => pipelines.deleteIfPresent(code));
    const pipeline = new PipelineDetailPage(page, code);
    const reportSubject = (state: string) => `Run report of ${code} (${state})`;
    const runId = () => page.url().match(/\/runs\/([0-9a-f-]{36})/)![1];

    await pipeline.gotoScheduling();
    const name = await pipeline.addRecipient("Error", reportRecipientName);
    const since = new Date();

    await test.step("a successful run sends nothing to an Error-level recipient", async () => {
      await pipelines.gotoPipeline(code);
      await pipelines.run();
      expect(await pipelines.waitForRunToFinish()).toBe("Succeeded");
    });

    let failedRunId: string;
    await test.step("a failed run is reported to them", async () => {
      await pipelines.gotoPipeline(code);
      await pipelines.runWith({ fail: true });
      expect(await pipelines.waitForRunToFinish()).toBe("Failed");
      failedRunId = runId();

      const report = await mailbox.waitForEmail(recipient, {
        since,
        subject: reportSubject("Failed"),
      });
      expect(report.text).toContain(code);
      expect(report.text).toContain("Failed");
      expect(linkTo(report, `${workspacePaths.pipelines}${code}/runs/${failedRunId}`)).toBeTruthy();
    });

    await test.step("and that is the only report so far", async () => {
      // Mailgun's events index is eventually consistent: a query made right
      // after an event can miss it, so the list is read until it settles.
      await expect
        .poll(
          async () =>
            (await mailbox.emailsSince(recipient, since))
              .map((email) => email.subject)
              .filter((subject) => subject.startsWith(`Run report of ${code}`)),
          { timeout: 60_000, intervals: [3_000] },
        )
        .toEqual([reportSubject("Failed")]);
    });

    await test.step("at level All, a successful run is reported too", async () => {
      await pipeline.gotoScheduling();
      await pipeline.removeRecipient(name);
      await pipeline.addRecipient("All", reportRecipientName);
      const sinceAll = new Date();

      await pipelines.gotoPipeline(code);
      await pipelines.run();
      expect(await pipelines.waitForRunToFinish()).toBe("Succeeded");
      const successRunId = runId();

      const report = await mailbox.waitForEmail(recipient, {
        since: sinceAll,
        subject: reportSubject("Success"),
      });
      expect(report.text).toContain("Success");
      expect(linkTo(report, `${workspacePaths.pipelines}${code}/runs/${successRunId}`)).toBeTruthy();
    });
  });
});
