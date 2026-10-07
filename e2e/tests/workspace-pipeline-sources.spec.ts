import { expect, test } from "../fixtures/cleanup";
import { uniqueName } from "../helpers/confirm";
import { PipelineDetailPage } from "../pages/PipelineDetailPage";
import { WorkspaceFilesPage } from "../pages/WorkspaceFilesPage";
import { WorkspacePipelinesPage } from "../pages/WorkspacePipelinesPage";

const NOTEBOOK_MARKER = "E2E-NOTEBOOK-RAN";

/** A notebook whose one cell logs a marker to the run. */
const NOTEBOOK = JSON.stringify({
  cells: [
    {
      cell_type: "code",
      execution_count: null,
      metadata: {},
      outputs: [],
      source: [
        "from openhexa.sdk import current_run\n",
        `current_run.log_info("${NOTEBOOK_MARKER}")\n`,
      ],
    },
  ],
  metadata: {
    kernelspec: { display_name: "Python 3", language: "python", name: "python3" },
  },
  nbformat: 4,
  nbformat_minor: 5,
});

/** Two tasks, the second fed by the first, for the task graph to draw. */
const TASKS_PIPELINE_SOURCE = `from openhexa.sdk import current_run, pipeline


@pipeline("e2e_tasks", name="E2E tasks pipeline")
def e2e_tasks():
    count = e2e_extract()
    e2e_report(count)


@e2e_tasks.task
def e2e_extract():
    return 3


@e2e_tasks.task
def e2e_report(count):
    current_run.log_info(f"E2E-TASKS {count}")


if __name__ == "__main__":
    e2e_tasks()
`;

test.describe("Pipeline sources", () => {
  test("a pipeline made from a notebook runs it", async ({ page, cleanup }) => {
    // A run, which provisions a container.
    test.setTimeout(420_000);
    const files = new WorkspaceFilesPage(page);
    const pipelines = new WorkspacePipelinesPage(page);
    const notebook = `${uniqueName("e2e-notebook")}.ipynb`;
    const name = uniqueName("e2e-from-notebook");

    await files.goto();
    await files.uploadFile(notebook, NOTEBOOK);
    cleanup.add(`file ${notebook}`, () => files.deleteIfPresent(notebook));
    // The name is unique and lower-case, so the code is the name.
    cleanup.add(`pipeline ${name}`, () => pipelines.deleteIfPresent(name));

    const code = await pipelines.createFromNotebook(name, notebook);
    if (code !== name) {
      cleanup.add(`pipeline ${code}`, () => pipelines.deleteIfPresent(code));
    }
    const pipeline = new PipelineDetailPage(page, code);

    await pipeline.gotoGeneral();
    await expect(pipeline.field("Notebook path")).toContainText(notebook);

    // A notebook takes no parameters, so Run starts it without a dialog.
    await pipelines.runButton.click();
    await page.waitForURL(/\/runs\/[0-9a-f-]{36}\/?$/);
    expect(await pipelines.waitForRunToFinish()).toBe("Succeeded");
    await expect(page.getByText(NOTEBOOK_MARKER)).toBeVisible();
  });

  test("a pipeline's tasks are drawn as a graph", async ({ page, cleanup }) => {
    const pipelines = new WorkspacePipelinesPage(page);
    const code = await pipelines.createWithSource(
      uniqueName("e2e-tasks"),
      TASKS_PIPELINE_SOURCE,
    );
    cleanup.add(`pipeline ${code}`, () => pipelines.deleteIfPresent(code));

    await new PipelineDetailPage(page, code).gotoGeneral();
    for (const task of ["e2e_extract", "e2e_report"]) {
      await expect(page.getByTitle(task, { exact: true })).toBeVisible();
    }
  });
});
