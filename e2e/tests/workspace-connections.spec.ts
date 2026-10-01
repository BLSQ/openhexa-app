import { expect, test } from "../fixtures/cleanup";
import { uniqueName } from "../helpers/confirm";
import {
  CONNECTION_TYPES,
  WorkspaceConnectionsPage,
} from "../pages/WorkspaceConnectionsPage";

test.describe("Workspace connections", () => {
  for (const type of CONNECTION_TYPES) {
    test(`a ${type} connection can be created and deleted`, async ({
      page,
      cleanup,
    }) => {
      const connections = new WorkspaceConnectionsPage(page);
      const name = uniqueName("e2e conn");

      await connections.goto();
      const id = await connections.create(type, name);
      cleanup.add(`connection ${name}`, () => connections.deleteIfPresent(id));

      await connections.expectVisible(name);

      await connections.gotoConnection(id);
      await connections.delete();
      await expect(connections.card(name)).toHaveCount(0);
    });
  }
});
