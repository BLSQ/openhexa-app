import { workspace } from "../config/environment";
import { expect, test } from "../fixtures/cleanup";
import { graphql } from "../helpers/graphql";
import { uniqueName } from "../helpers/confirm";
import {
  CONNECTION_TYPES,
  WorkspaceConnectionsPage,
} from "../pages/WorkspaceConnectionsPage";
import { WorkspacePipelinesPage } from "../pages/WorkspacePipelinesPage";

const CONNECTION_MARKER = "E2E-CONNECTION-QUERIED";

/** Queries the database behind a PostgreSQL connection given as a parameter. */
const CONNECTION_PIPELINE_SOURCE = `from openhexa.sdk import PostgreSQLConnection, current_run, parameter, pipeline
from sqlalchemy import create_engine, text


@pipeline("e2e_connection", name="E2E connection pipeline")
@parameter("db", name="Database", type=PostgreSQLConnection, required=True)
def e2e_connection(db):
    with create_engine(db.url).connect() as connection:
        value = connection.execute(text("SELECT 41 + 1")).scalar()
    current_run.log_info(f"${CONNECTION_MARKER} {db.database_name} {value}")


if __name__ == "__main__":
    e2e_connection()
`;

type Credentials = {
  host: string;
  port: number;
  dbName: string;
  username: string;
  password: string;
};

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

  test("a PostgreSQL connection is tested, edited and used by a pipeline", async ({
    page,
    cleanup,
  }) => {
    // A pipeline run, which provisions a container.
    test.setTimeout(420_000);
    const connections = new WorkspaceConnectionsPage(page);
    const pipelines = new WorkspacePipelinesPage(page);
    const name = uniqueName("e2e conn");

    // The workspace's own database is the one real PostgreSQL server the
    // suite can count on reaching.
    await connections.goto();
    const { workspace: ws } = await graphql<{
      workspace: { database: { credentials: Credentials } };
    }>(
      page,
      `query ($slug: String!) {
        workspace(slug: $slug) {
          database { credentials { host port dbName username password } }
        }
      }`,
      { slug: workspace.slug },
    );
    const credentials = ws.database.credentials;

    const id = await connections.create("PostgreSQL", name);
    cleanup.add(`connection ${name}`, () => connections.deleteIfPresent(id));

    await test.step("a wrong password fails the test", async () => {
      await connections.editFields({
        "Database name": credentials.dbName,
        Host: credentials.host,
        Port: String(credentials.port),
        Username: credentials.username,
        Password: "not-the-password",
      });
      await expect(await connections.testConnection()).toHaveText(
        /Connection failed/,
      );
      await connections.cancelFields();
    });

    await test.step("the right one passes, and is kept hidden", async () => {
      await connections.editFields({
        "Database name": credentials.dbName,
        Host: credentials.host,
        Port: String(credentials.port),
        Username: credentials.username,
        Password: credentials.password,
      });
      await expect(await connections.testConnection()).toHaveText(
        "Connection successful!",
      );
      await connections.saveFields();

      await page.reload();
      await expect(connections.fieldValue("db_name")).toContainText(
        credentials.dbName,
      );
      await expect(connections.fieldValue("password")).toHaveText(/^\*+$/);
      await expect(page.getByText(credentials.password)).toHaveCount(0);
    });

    await test.step("a pipeline given it as a parameter queries it", async () => {
      const code = await pipelines.createWithSource(
        uniqueName("e2e-connection"),
        CONNECTION_PIPELINE_SOURCE,
      );
      cleanup.add(`pipeline ${code}`, () => pipelines.deleteIfPresent(code));

      await pipelines.gotoPipeline(code);
      await pipelines.runWith({ db: name });
      expect(await pipelines.waitForRunToFinish()).toBe("Succeeded");
      await expect(
        page.getByText(`${CONNECTION_MARKER} ${credentials.dbName} 42`),
      ).toBeVisible();
    });
  });
});
