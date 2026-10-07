import { Locator, Page, expect } from "@playwright/test";

import { workspace, workspacePaths } from "../config/environment";

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
  async createWithSource(name: string, source: string): Promise<string> {
    await this.goto();
    const response = await this.page.evaluate(
      async ({ workspaceSlug, name, source }) => {
        const csrf = document.cookie.match(/csrftoken=([^;]+)/)?.[1] ?? "";
        const res = await fetch("/graphql/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrf,
          },
          body: JSON.stringify({
            query: `mutation ($input: CreatePipelineInput!) {
              createPipeline(input: $input) {
                success
                errors
                details
                pipeline { code }
              }
            }`,
            variables: {
              input: {
                workspaceSlug,
                name,
                version: { files: [{ path: "pipeline.py", content: source }] },
              },
            },
          }),
        });
        return res.json();
      },
      { workspaceSlug: workspace.slug, name, source },
    );
    const result = response?.data?.createPipeline;
    expect(result?.success, JSON.stringify(response)).toBe(true);
    return result.pipeline.code;
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

  /** The run page reports status inside its level-3 heading. */
  get runStatus(): Locator {
    return this.page.getByRole("heading", { level: 3 });
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
