import { Locator, Page, expect } from "@playwright/test";

import { workspace, workspacePaths } from "../config/environment";
import { graphql } from "../helpers/graphql";

export const PIPELINE_TABS = [
  "General",
  "Runs",
  "Scheduling and Notifications",
  "Code",
] as const;

export type PipelineTab = (typeof PIPELINE_TABS)[number];

/** A run is finished once its status reads one of these. */
const TERMINAL_STATUS = /Succeeded|Failed|Stopped|Terminated/;

export const EDITED_PIPELINE_MARKER = "E2E_EDITED_VERSION";

/**
 * Replaces a template's code with a pipeline that only logs. The decorator's own
 * code and name do not have to match the pipeline they are uploaded to, so this
 * works whichever template the catalogue offers first -- and unlike the template
 * it replaces, it reaches no external service, so its run is expected to succeed.
 */
export const EDITED_PIPELINE_SOURCE = `from openhexa.sdk.pipelines import current_run, pipeline


@pipeline("e2e_edited", name="E2E edited pipeline")
def e2e_edited():
    current_run.log_info("${EDITED_PIPELINE_MARKER}")


if __name__ == "__main__":
    e2e_edited()
`;

/** What `RUN_PIPELINE_SOURCE` logs, once per run, with its parameters. */
export const PARAMETERS_MARKER = "E2E-PARAMETERS";

/** What `RUN_PIPELINE_SOURCE` logs every few seconds while it holds. */
export const HOLDING_MARKER = "E2E-HOLDING";

/**
 * A pipeline for exercising runs: typed parameters it logs back, an optional
 * hold that keeps it running (and logging) for a while, and an optional
 * `output` under which it writes a CSV file and a database table and records
 * both as run outputs.
 */
export const RUN_PIPELINE_SOURCE = `import time

import pandas as pd
from openhexa.sdk import current_run, parameter, pipeline, workspace
from sqlalchemy import create_engine


@pipeline("e2e_run", name="E2E run pipeline")
@parameter("rows", name="Rows", type=int, default=2, required=True)
@parameter("label", name="Label", type=str, choices=["alpha", "beta"], default="alpha", required=True)
@parameter("shout", name="Shout", type=bool, default=False, required=False)
@parameter("hold", name="Hold seconds", type=int, default=0, required=False)
@parameter("output", name="Output name", type=str, required=False)
def e2e_run(rows, label, shout, hold, output):
    text = label.upper() if shout else label
    current_run.log_info(f"${PARAMETERS_MARKER} rows={rows} label={text}")
    for second in range(0, hold or 0, 5):
        current_run.log_info(f"${HOLDING_MARKER} {second}s")
        time.sleep(5)
    if output:
        frame = pd.DataFrame({"n": range(rows), "label": [text] * rows})
        path = f"{workspace.files_path}/{output}.csv"
        frame.to_csv(path, index=False)
        current_run.add_file_output(path)
        frame.to_sql(output, create_engine(workspace.database_url), if_exists="replace", index=False)
        current_run.add_database_output(output)


if __name__ == "__main__":
    e2e_run()
`;

export class WorkspacePipelinesPage {
  constructor(private readonly page: Page) {}

  get templatesTable(): Locator {
    return this.page.getByRole("tabpanel", { name: "Available Templates" });
  }

  get deleteButton(): Locator {
    return this.page.getByRole("button", { name: "Delete", exact: true });
  }

  get deleteDialog(): Locator {
    return this.page.getByRole("dialog").filter({
      has: this.page.getByRole("heading", { name: "Delete pipeline" }),
    });
  }

  row(name: string): Locator {
    return this.page
      .getByRole("row")
      .filter({ has: this.page.getByRole("link", { name, exact: true }) });
  }

  async goto() {
    await this.page.goto(workspacePaths.pipelines);
  }

  async gotoTemplates() {
    await this.page.goto(`${workspacePaths.pipelines}?tab=templates`);
    await expect(
      this.templatesTable
        .getByRole("button", { name: "Create pipeline" })
        .first(),
    ).toBeVisible();
  }

  /**
   * Builds a pipeline from the first template on offer. The catalogue is shared
   * demo data, so the test takes whatever is listed first rather than naming a
   * template that may be renamed or unpublished.
   */
  async createFromFirstTemplate(): Promise<{ name: string; code: string }> {
    await this.gotoTemplates();

    const firstRow = this.templatesTable.getByRole("row").nth(1);
    const name = (await firstRow.getByRole("link").first().innerText()).trim();

    await firstRow.getByRole("button", { name: "Create pipeline" }).click();
    await this.page.waitForURL(
      (url) =>
        /\/pipelines\/[^/]+\/?$/.test(url.pathname) &&
        !url.search.includes("tab="),
    );

    const code = this.page.url().replace(/\/$/, "").split("/pipelines/")[1];
    return { name, code };
  }

  /**
   * Creates a pipeline whose first version is `source`, through the API: the
   * tests that need one to work on get a known file under a unique name,
   * rather than a template's, which two tests at once would collide over.
   * Returns its code.
   */
  async createWithSource(
    name: string,
    source: string,
    workspaceSlug = workspace.slug,
  ): Promise<string> {
    await this.goto();
    const data = await graphql(
      this.page,
      `mutation ($input: CreatePipelineInput!) {
        createPipeline(input: $input) { success errors details pipeline { code } }
      }`,
      {
        input: {
          workspaceSlug,
          name,
          version: { files: [{ path: "pipeline.py", content: source }] },
        },
      },
    );
    expect(data.createPipeline.success, JSON.stringify(data)).toBe(true);
    return data.createPipeline.pipeline.code;
  }

  /** Publishes `source` as the pipeline's next version, through the API. */
  async uploadVersion(
    code: string,
    source: string,
    workspaceSlug = workspace.slug,
  ) {
    const data = await graphql(
      this.page,
      `mutation ($input: UploadPipelineInput!) {
        uploadPipeline(input: $input) { success errors details }
      }`,
      {
        input: {
          workspaceSlug,
          pipelineCode: code,
          files: [{ path: "pipeline.py", content: source }],
        },
      },
    );
    expect(data.uploadPipeline.success, JSON.stringify(data)).toBe(true);
  }

  async gotoPipeline(code: string) {
    await this.page.goto(`${workspacePaths.pipelines}${code}/`);
  }

  async gotoCode(code: string) {
    await this.page.goto(`${workspacePaths.pipelines}${code}/code/`);
  }

  tab(name: PipelineTab): Locator {
    return this.page.getByRole("link", { name, exact: true });
  }

  async openTab(name: PipelineTab) {
    await this.tab(name).click();
  }

  async gotoVersions(code: string) {
    await this.page.goto(`${workspacePaths.pipelines}${code}/versions/`);
  }

  /** A card's heading on the versions page, e.g. "Version v2". */
  versionHeading(version: string): Locator {
    return this.page.getByRole("heading", {
      name: new RegExp(`Version ${version}\\b`),
    });
  }

  // --- running -------------------------------------------------------------

  get runButton(): Locator {
    return this.page.getByRole("button", { name: "Run", exact: true });
  }

  get runDialog(): Locator {
    return this.page.getByRole("dialog").filter({
      has: this.page.getByRole("heading", { name: "Run pipeline" }),
    });
  }

  /** Starts a run and waits for the redirect to its page. */
  async run() {
    await this.runButton.click();
    await this.runDialog
      .getByRole("button", { name: "Run", exact: true })
      .click();
    await this.page.waitForURL(/\/runs\/[0-9a-f-]{36}\/?$/);
  }

  /**
   * A parameter's field in the run (or default values) dialog. The label points at the input by
   * the parameter's code; the switch and combobox widgets carry no name of
   * their own, so the field is reached through the label.
   */
  parameterField(code: string, form: Locator = this.runDialog): Locator {
    return form
      .locator(`label[for="${code}"]`)
      .locator("xpath=ancestor::div[2]");
  }

  /**
   * Numbers and text are typed, choices picked, and a boolean switched. The
   * default-values dialog lays its fields out the same way as the run dialog.
   */
  async fillParameters(
    values: Record<string, string | number | boolean>,
    form: Locator = this.runDialog,
  ) {
    for (const [code, value] of Object.entries(values)) {
      const field = this.parameterField(code, form);
      if (typeof value === "boolean") {
        const toggle = field.getByRole("switch");
        if ((await toggle.getAttribute("aria-checked")) !== String(value)) {
          await toggle.click();
        }
        await expect(toggle).toHaveAttribute("aria-checked", String(value));
      } else if (await field.getByRole("combobox").count()) {
        await field.getByRole("combobox").click();
        await this.page
          .getByRole("option", { name: String(value), exact: true })
          .click();
      } else {
        await field.locator(`input[name="${code}"]`).fill(String(value));
      }
    }
  }

  /** Starts a run with these parameters and waits for its page. */
  async runWith(values: Record<string, string | number | boolean>) {
    await this.runButton.click();
    await expect(this.runDialog).toBeVisible();
    await this.fillParameters(values);
    await this.runDialog
      .getByRole("button", { name: "Run", exact: true })
      .click();
    await this.page.waitForURL(/\/runs\/[0-9a-f-]{36}\/?$/);
  }

  get stopButton(): Locator {
    return this.page.getByRole("button", { name: "Stop", exact: true });
  }

  get stopDialog(): Locator {
    return this.page.getByRole("dialog").filter({
      has: this.page.getByRole("heading", { name: /^Stop .* execution$/ }),
    });
  }

  async stopRun() {
    await this.stopButton.click();
    await this.stopDialog
      .getByRole("button", { name: "Stop", exact: true })
      .click();
    await expect(this.stopDialog).toBeHidden();
  }

  /** A row of the run's Outputs table, by the output's exact name. */
  outputRow(name: string): Locator {
    return this.page
      .getByRole("row")
      .filter({ has: this.page.getByText(name, { exact: true }) });
  }

  /** The run page reports status inside its level-3 heading. */
  get runStatus(): Locator {
    return this.page.getByRole("main").getByRole("heading", { level: 3 });
  }

  /** Waits for the run to finish and returns the status it settled on. */
  async waitForRunToFinish(timeout = 300_000): Promise<string> {
    await expect(this.runStatus).toContainText(TERMINAL_STATUS, { timeout });
    const heading = await this.runStatus.innerText();
    return TERMINAL_STATUS.exec(heading)![0];
  }

  /** A <dt>/<dd> pair on the run page, e.g. "Version" or "Trigger". */
  runDetail(term: string): Locator {
    return this.page
      .getByRole("term")
      .filter({ hasText: term })
      .locator("xpath=following-sibling::dd");
  }

  get runMessages(): Locator {
    return this.page.getByRole("table");
  }

  // --- editing -------------------------------------------------------------

  /** CodeMirror's content area. Filling it replaces the whole file. */
  get codeEditor(): Locator {
    return this.page.locator(".cm-content");
  }

  get saveCodeButton(): Locator {
    return this.page.getByRole("button", { name: "Save", exact: true });
  }

  filesHeading(version: string): Locator {
    return this.page.getByRole("heading", { name: `Files - ${version}` });
  }

  /** Rewrites pipeline.py and saves, which publishes a new version. */
  async editCode(code: string, source: string) {
    await this.gotoPipeline(code);
    await this.openTab("Code");

    await expect(this.codeEditor).toBeVisible();
    await this.codeEditor.fill(source);

    // Save only appears once there are pending changes, and goes again once
    // they are committed.
    await this.saveCodeButton.click();
    await expect(this.saveCodeButton).toBeHidden();
  }

  async delete() {
    await this.deleteButton.click();
    await this.deleteDialog.getByRole("button", { name: "Delete" }).click();
    await this.page.waitForURL(`**${workspacePaths.pipelines}`);
  }

  async deleteIfPresent(code: string) {
    const response = await this.page.goto(
      `${workspacePaths.pipelines}${code}/`,
    );
    if (response?.status() === 404) {
      return;
    }
    await this.delete();
  }
}
