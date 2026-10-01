import { expect, test } from "../fixtures/cleanup";
import { uniqueName } from "../helpers/confirm";
import {
  WebappType,
  WorkspaceWebappsPage,
} from "../pages/WorkspaceWebappsPage";

const TYPES: WebappType[] = ["iFrame", "Static"];

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
});
