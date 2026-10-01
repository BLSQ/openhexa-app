import { expect, test } from "../fixtures/cleanup";
import { uniqueName } from "../helpers/confirm";
import { WorkspaceFilesPage } from "../pages/WorkspaceFilesPage";

test.describe("Workspace files", () => {
  test("a folder can be created and deleted", async ({ page, cleanup }) => {
    const files = new WorkspaceFilesPage(page);
    const folder = uniqueName("e2e-folder");

    await files.goto();
    await files.createFolder(folder);
    cleanup.add(`folder ${folder}`, () => files.deleteIfPresent(folder));
    await expect(files.row(folder)).toBeVisible();

    await files.delete(folder);
  });

  test("a file can be uploaded and deleted", async ({ page, cleanup }) => {
    const files = new WorkspaceFilesPage(page);
    const fileName = `${uniqueName("e2e-file")}.csv`;

    await files.goto();
    await files.uploadFile(fileName, "id,value\n1,ok\n");
    cleanup.add(`file ${fileName}`, () => files.deleteIfPresent(fileName));
    await expect(files.row(fileName)).toBeVisible();

    await files.delete(fileName);
  });
});
