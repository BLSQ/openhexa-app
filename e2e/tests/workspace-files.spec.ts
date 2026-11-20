import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";

import { mergeTests } from "@playwright/test";

import { test as disposableTest } from "../fixtures/disposableWorkspace";
import { expect, test as visitorsTest } from "../fixtures/visitors";
import { uniqueName } from "../helpers/confirm";
import { WorkspaceFilesPage } from "../pages/WorkspaceFilesPage";
import { WorkspaceSettingsPage } from "../pages/WorkspaceSettingsPage";

const test = mergeTests(visitorsTest, disposableTest);

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
      // eslint-disable-next-line playwright/prefer-to-have-length -- a failure would print the whole file
      expect(body.length, `${name} came back whole`).toBe(contents.length);
    }

    await files.delete(accented);
    await files.delete(large);
  });

  test("the public folder's files are served to anyone, once the workspace allows it", async ({
    page,
    anonymousPage,
    disposableWorkspace,
  }) => {
    test.setTimeout(300_000);
    await page.goto("/");
    test.skip(
      !(await new WorkspaceFilesPage(page).publicFilesOffered()),
      "The instance does not offer public files (PUBLIC_FILES_ENABLED).",
    );

    const slug = await disposableWorkspace.create();
    const files = new WorkspaceFilesPage(page, slug);
    const settings = new WorkspaceSettingsPage(page);
    const visitor = anonymousPage.request;
    const fileName = "regions.csv";
    const contents = "code,name\nDK,Dakar\n";
    let link = "";

    await test.step("a placeholder offers to create the folder", async () => {
      await files.goto();
      await expect(files.publicFolderPlaceholder).toContainText(
        "Enable public files and create this folder to start sharing files publicly",
      );
      await files.createPublicFolder();
      await files.uploadFile(fileName, contents);
      await files.uploadFile(".hidden.csv", contents);
      await expect(files.row(fileName)).toBeVisible();
    });

    await test.step("nothing is shared while the setting is off", async () => {
      await expect(files.copyPublicLinkButton(fileName)).toHaveCount(0);
      const response = await visitor.get(`/files/${slug}/public/${fileName}`);
      expect(response.status()).toBe(404);

      await files.goto();
      await expect(files.publicFolderPlaceholder).toHaveCount(0);
      await expect(files.publicFolderStatus("Not shared publicly")).toBeVisible();
    });

    await test.step("the folder's lock leads an admin to the setting", async () => {
      await files.publicFolderStatus("Not shared publicly").click();
      await page.waitForURL(`**/workspaces/${slug}/settings/`);
      await expect(settings.publicFilesSwitch).not.toBeChecked();
      await settings.setPublicFiles(true);

      await files.goto();
      await expect(files.publicFolderStatus("Shared publicly")).toBeVisible();
    });

    await test.step("a file's link is copied from its row", async () => {
      await files.openFolder("public");
      link = await files.copyPublicLink(fileName);
      expect(new URL(link).pathname).toBe(`/files/${slug}/public/${fileName}`);
    });

    await test.step("a visitor without an account downloads it, from any site", async () => {
      const redirect = await visitor.get(link, { maxRedirects: 0 });
      expect(redirect.status()).toBe(302);
      expect(redirect.headers()["access-control-allow-origin"]).toBe("*");

      const response = await visitor.get(link);
      expect(response.status()).toBe(200);
      expect(await response.text()).toBe(contents);
    });

    await test.step("the folder is not listed, and hidden or missing files are not served", async () => {
      for (const path of ["", ".hidden.csv", "missing.csv"]) {
        const response = await visitor.get(
          new URL(`/files/${slug}/public/${path}`, link).href,
        );
        expect(response.status(), path || "the folder").toBe(404);
      }
    });

    await test.step("turning the setting off locks the folder again", async () => {
      await settings.gotoTab(slug, "General");
      await settings.setPublicFiles(false);

      await files.goto();
      await expect(files.publicFolderStatus("Not shared publicly")).toBeVisible();
      await files.openFolder("public");
      await expect(files.row(fileName)).toBeVisible();
      await expect(files.copyPublicLinkButton(fileName)).toHaveCount(0);

      const response = await visitor.get(link);
      expect(response.status()).toBe(404);
    });
  });
});
