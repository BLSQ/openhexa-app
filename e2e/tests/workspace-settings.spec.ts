import { mergeTests } from "@playwright/test";

import { credentials, workspace } from "../config/environment";
import { test as cleanupTest } from "../fixtures/cleanup";
import { expect, test as disposableTest } from "../fixtures/disposableWorkspace";
import { test as mailboxTest } from "../fixtures/mailbox";
import { test as visitorsTest } from "../fixtures/visitors";
import { uniqueName } from "../helpers/confirm";
import { linkTo, mailboxAddress } from "../helpers/mailbox";
import { OrganizationExternalCollaboratorsPage } from "../pages/OrganizationExternalCollaboratorsPage";
import { RegisterPage } from "../pages/RegisterPage";
import { WorkspacePipelinesPage } from "../pages/WorkspacePipelinesPage";
import { WorkspaceSettingsPage } from "../pages/WorkspaceSettingsPage";

const test = mergeTests(cleanupTest, disposableTest, mailboxTest, visitorsTest);

const CONFIG_MARKER = "E2E-CONFIG";
const DATABASE_MARKER = "E2E-DATABASE-WRITTEN";

/**
 * Reports what a run sees of the workspace: its configuration, read through
 * the SDK, and its database, written with the credentials the run is given.
 */
const SETTINGS_PIPELINE_SOURCE = `from openhexa.sdk import current_run, pipeline, workspace
from sqlalchemy import create_engine, text


@pipeline("e2e_settings", name="E2E settings pipeline")
def e2e_settings():
    current_run.log_info(f"${CONFIG_MARKER} {workspace.configuration}")
    with create_engine(workspace.database_url).begin() as connection:
        connection.execute(text("CREATE TABLE IF NOT EXISTS e2e_settings (n integer)"))
    current_run.log_info("${DATABASE_MARKER}")


if __name__ == "__main__":
    e2e_settings()
`;

test.describe("Workspace settings", () => {
  test("its general settings change, and runs see them", async ({
    page,
    disposableWorkspace,
  }) => {
    // Provisioning a workspace, then a pipeline run in it.
    test.setTimeout(420_000);
    const settings = new WorkspaceSettingsPage(page);
    const pipelines = new WorkspacePipelinesPage(page);
    const configValue = uniqueName("e2e-value");

    const slug = await disposableWorkspace.create();
    const newName = `${disposableWorkspace.name} renamed`;

    await test.step("its name, countries and configuration are saved", async () => {
      await settings.gotoTab(slug, "General");
      await settings.editButton.click();
      await settings.field("Name").getByRole("textbox").fill(newName);
      await settings.addCountry("Senegal");
      await settings.addConfiguration("e2e_key", configValue);
      await settings.save();

      await settings.gotoTab(slug, "General");
      await expect(settings.field("Name")).toHaveText(newName);
      await expect(settings.field("Countries")).toContainText("Senegal");
      await expect(settings.field("Configuration")).toContainText("e2e_key");
      await expect(settings.field("Configuration")).toContainText(configValue);
    });

    await test.step("the database passwords are regenerated", async () => {
      await settings.gotoTab(slug, "Database");
      await settings.regeneratePassword("ro");
      await settings.regeneratePassword("rw");
    });

    await test.step("a run reads the configuration and writes to the database", async () => {
      const code = await pipelines.createWithSource(
        uniqueName("e2e-settings"),
        SETTINGS_PIPELINE_SOURCE,
        slug,
      );
      await page.goto(`/workspaces/${slug}/pipelines/${code}/`);
      await pipelines.run();

      expect(await pipelines.waitForRunToFinish()).toBe("Succeeded");
      await expect(page.getByText(new RegExp(`${CONFIG_MARKER} .*${configValue}`))).toBeVisible();
      // Written with the password regenerated above.
      await expect(page.getByText(DATABASE_MARKER)).toBeVisible();
    });
  });

  test("an address without an account is invited by email, resent to, and the invitation deleted", async ({
    page,
    anonymousPage,
    cleanup,
    mailbox,
  }) => {
    const settings = new WorkspaceSettingsPage(page);
    const collaborators = new OrganizationExternalCollaboratorsPage(page);
    // The register page turns a signed-in visitor away, so it is a stranger who opens the link.
    const register = new RegisterPage(anonymousPage);
    // Only the invitation is exercised: registering would leave an account behind.
    const address = mailboxAddress("e2e-wsinvite");
    cleanup.add(`workspace invitation for ${address}`, () =>
      settings.deleteInvitationIfPresent(workspace.slug, address),
    );

    let since = new Date();
    await settings.goto(workspace.slug);
    await settings.addMember(address, "Viewer");
    await expect(settings.invitationRow(address)).toContainText("Viewer");
    await expect(settings.invitationRow(address)).toContainText("Pending");

    const invitation = await mailbox.waitForEmail(address, {
      since,
      subject: `You've been invited to join the workspace ${workspace.name} on OpenHEXA`,
    });
    expect(invitation.text).toContain(credentials.email);
    const link = linkTo(invitation, "/register");
    expect(link.searchParams.get("email")).toBe(address);

    await test.step("the organization lists it as a direct workspace invitation", async () => {
      await collaborators.goto();
      await expect(collaborators.pendingInvitationRow(address)).toContainText(
        "Viewer",
      );
    });

    await test.step("resending issues a new link", async () => {
      since = new Date();
      await settings.goto(workspace.slug);
      await settings.resendInvitation(address);
      const resent = await mailbox.waitForEmail(address, {
        since,
        subject: invitation.subject,
      });
      expect(linkTo(resent, "/register").searchParams.get("token")).not.toBe(
        link.searchParams.get("token"),
      );
    });

    await test.step("the link opens the registration form for that address", async () => {
      await register.open(link);
      await expect(register.emailInput).toHaveValue(address);
    });

    await test.step("deleting it empties the list", async () => {
      await settings.goto(workspace.slug);
      await settings.deleteInvitation(address);
      await page.reload();
      await expect(settings.invitationRow(address)).toHaveCount(0);
    });
  });
});
