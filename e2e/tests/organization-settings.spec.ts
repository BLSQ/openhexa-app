import { expect, test } from "@playwright/test";

import { organization, organizationPaths } from "../config/environment";
import { OrganizationSettingsPage } from "../pages/OrganizationSettingsPage";

test.describe("Organization settings", () => {
  let settings: OrganizationSettingsPage;

  test.beforeEach(async ({ page }) => {
    settings = new OrganizationSettingsPage(page);
    await settings.goto();
    await expect(settings.heading).toBeVisible();
  });

  test("renders every settings card", async () => {
    await expect(settings.generalCard).toBeVisible();
    await expect(settings.aiAssistantCard).toBeVisible();
    await expect(settings.usageAndLimitsCard).toBeVisible();
  });

  test("the General card shows the organization identity", async () => {
    await expect(settings.generalValue("Organization Name")).toHaveText(
      organization.name,
    );
    await expect(settings.generalValue("Short Name")).toHaveText(
      organization.shortName,
    );
    await expect(settings.generalValue("Organization Logo")).toBeVisible();
  });

  test("the Usage & Limits card reports each quota", async () => {
    for (const metric of [
      "Users",
      "Workspaces",
      "Pipeline Runs (this month)",
      "AI Usage in USD (this month)",
    ]) {
      await expect(settings.usageMetric(metric)).toHaveText(/^[\d.]+$/);
    }
    await expect(settings.manageSubscriptionLink).toHaveAttribute(
      "href",
      /^https?:\/\//,
    );
  });

  test("the AI Assistant card reports its configuration", async () => {
    await expect(settings.aiAssistantCard.getByText("Enabled")).toBeVisible();
    await expect(settings.aiAssistantCard.getByText("Provider")).toBeVisible();
    await expect(settings.aiAssistantCard.getByRole("switch")).toHaveCount(1);
  });

  test("Edit opens the General form prefilled and Cancel discards it", async () => {
    await settings.editGeneralButton.click();

    await expect(settings.nameInput).toHaveValue(organization.name);
    await expect(settings.shortNameInput).toHaveValue(organization.shortName);
    await expect(settings.saveChangesButton).toBeVisible();

    // Type into the form and back out: the read-only view must come back with
    // the stored values, and nothing may be persisted.
    await settings.nameInput.fill(`${organization.name} (edited)`);
    await settings.cancelButton.click();

    await expect(settings.nameInput).toBeHidden();
    await expect(settings.editGeneralButton).toBeVisible();
    await expect(settings.generalValue("Organization Name")).toHaveText(
      organization.name,
    );
  });

  test("the short name field coerces its input", async () => {
    await settings.editGeneralButton.click();

    // Nothing here submits: the suite runs against a shared environment, so it
    // exercises the client-side rules and backs out again.
    await settings.shortNameInput.fill("lower");
    await expect(settings.shortNameInput).toHaveValue("LOWER");

    await settings.shortNameInput.fill("toolongshortname");
    await expect(settings.shortNameInput).toHaveValue("TOOLO");

    await settings.cancelButton.click();
    await expect(settings.generalValue("Short Name")).toHaveText(
      organization.shortName,
    );
  });

  test("settings is reachable from the sidebar", async ({ page }) => {
    await page.goto(organizationPaths.workspaces);
    await settings.sidebar.open("Settings");

    await expect(page).toHaveURL(new RegExp(`${organizationPaths.settings}$`));
    await expect(settings.heading).toBeVisible();
  });
});
