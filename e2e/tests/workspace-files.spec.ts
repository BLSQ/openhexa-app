import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";

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

  test("a folder is browsed, searched and downloaded from", async ({
    page,
    cleanup,
  }) => {
    const files = new WorkspaceFilesPage(page);
    const folder = uniqueName("e2e-folder");
    const fileName = `${uniqueName("e2e-nested")}.csv`;

    await files.goto();
    await files.createFolder(folder);
    cleanup.add(`folder ${folder}`, () => files.deleteIfPresent(folder));

    await test.step("a file is uploaded inside it", async () => {
      await files.openFolder(folder);
      await files.uploadFile(fileName, "id,value\n1,nested\n");
      await files.uploadFile("other.csv", "id,value\n2,other\n");
      await expect(files.row(fileName)).toBeVisible();
      await expect(files.row("other.csv")).toBeVisible();
    });

    await test.step("it downloads with its name", async () => {
      const download = await files.download(fileName);
      expect(download.suggestedFilename()).toBe(fileName);
    });

    await test.step("searching the folder narrows it to the match", async () => {
      // The search only looks at the folder being shown, not below it.
      await files.search(fileName);
      await expect(files.row(fileName)).toBeVisible();
      await expect(files.row("other.csv")).toHaveCount(0);
    });

    await test.step("the breadcrumb leads back to the root", async () => {
      await files.breadcrumb("Files").click();
      await expect(files.row(folder)).toBeVisible();
      await expect(files.row(fileName)).toHaveCount(0);
    });
  });

  test("a whole folder is uploaded", async ({ page, cleanup }, testInfo) => {
    const files = new WorkspaceFilesPage(page);
    const folder = uniqueName("e2e-upload");
    const local = path.join(testInfo.outputPath(), folder);
    mkdirSync(local, { recursive: true });
    writeFileSync(path.join(local, "first.csv"), "id\n1\n");
    writeFileSync(path.join(local, "second.csv"), "id\n2\n");

    await files.goto();
    cleanup.add(`folder ${folder}`, () => files.deleteIfPresent(folder));
    await files.uploadDirectory(local);

    await files.goto();
    await files.openFolder(folder);
    await expect(files.row("first.csv")).toBeVisible();
    await expect(files.row("second.csv")).toBeVisible();
  });

  test("an accented name and a large file come back intact", async ({
    page,
    cleanup,
  }) => {
    test.setTimeout(180_000);
    const files = new WorkspaceFilesPage(page);
    const accented = `${uniqueName("e2e données")} région.csv`;
    const large = `${uniqueName("e2e-large")}.csv`;
    const largeContents = "id,value\n" + "1,abcdefghij\n".repeat(400_000);

    await files.goto();
    await files.uploadFile(accented, "id,ville\n1,Thiès\n");
    cleanup.add(`file ${accented}`, () => files.deleteIfPresent(accented));
    await files.uploadFile(large, largeContents);
    cleanup.add(`file ${large}`, () => files.deleteIfPresent(large));

    for (const [name, contents] of [
      [accented, "id,ville\n1,Thiès\n"],
      [large, largeContents],
    ]) {
      await expect(files.row(name)).toBeVisible();
      const download = await files.download(name);
      expect(download.suggestedFilename()).toBe(name);
      const body = readFileSync((await download.path())!, "utf8");
      expect(body.length, `${name} came back whole`).toBe(contents.length);
    }

    await files.delete(accented);
    await files.delete(large);
  });
});
