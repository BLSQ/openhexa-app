import { expect, test } from "../fixtures/cleanup";
import { uniqueName } from "../helpers/confirm";
import {
  WebappType,
  WorkspaceWebappsPage,
} from "../pages/WorkspaceWebappsPage";

// Static apps have their own, fuller spec: workspace-static-webapps.spec.ts.
const TYPES: WebappType[] = ["iFrame"];

test.describe("Workspace web apps", () => {
  for (const type of TYPES) {
    test(`a ${type} web app can be created and deleted`, async ({
      page,
      cleanup,
    }) => {
      const webapps = new WorkspaceWebappsPage(page);
      const name = uniqueName("e2e app");

      const slug = await webapps.create(type, name);
      cleanup.add(`web app ${name}`, () => webapps.deleteIfPresent(slug));

      await webapps.expectVisible(name);

      await webapps.gotoWebapp(slug);
      await webapps.delete();
      await expect(webapps.row(name)).toHaveCount(0);
    });
  }

  test("an iFrame app frames its URL, and follows a new one", async ({
    page,
    cleanup,
  }) => {
    const webapps = new WorkspaceWebappsPage(page);
    const name = uniqueName("e2e app");

    // Created pointing at https://example.com/.
    const slug = await webapps.create("iFrame", name);
    cleanup.add(`web app ${name}`, () => webapps.deleteIfPresent(slug));

    await webapps.gotoPlay(slug);
    await expect(webapps.playFrame).toHaveAttribute("src", "https://example.com/");

    await webapps.gotoTab(slug, "General");
    await webapps.updateDetails({ sourceUrl: "https://example.org/" });

    await webapps.gotoPlay(slug);
    await expect(webapps.playFrame).toHaveAttribute("src", "https://example.org/");
  });
});
