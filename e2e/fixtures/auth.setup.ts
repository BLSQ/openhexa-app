import { expect, test as setup } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

import {
  OUTSIDER_STORAGE_STATE,
  STORAGE_STATE,
  credentials,
  organization,
  outsiderCredentials,
} from "../config/environment";
import { LoginPage } from "../pages/LoginPage";

/**
 * Signs in once per run and hands the session to every other project through
 * `storageState`, so the suite pays the login cost a single time.
 */
setup("authenticate", async ({ page }) => {
  const loginPage = new LoginPage(page);

  await loginPage.goto();
  await loginPage.login(credentials.email, credentials.password);

  // A successful sign-in leaves /login for the landing page. Assert on that
  // rather than on a selector, so bad credentials fail here with a clear
  // message instead of somewhere downstream.
  await expect(page).not.toHaveURL(/\/login/, { timeout: 30_000 });
  await expect(
    page.getByRole("button", { name: credentials.email }),
  ).toBeVisible();

  // The suite assumes the test account can still reach the organization; a lost
  // membership or a revoked role should fail here, not in every test.
  await page.goto(`/organizations/${organization.id}/`);
  await expect(
    page.getByRole("heading", { name: organization.name, level: 1 }),
  ).toBeVisible();

  fs.mkdirSync(path.dirname(STORAGE_STATE), { recursive: true });
  await page.context().storageState({ path: STORAGE_STATE });
});

setup("authenticate the outsider", async ({ page }) => {
  setup.skip(
    !outsiderCredentials,
    "E2E_OUTSIDER_EMAIL / E2E_OUTSIDER_PASSWORD are not set",
  );
  const loginPage = new LoginPage(page);

  await loginPage.goto();
  await loginPage.login(
    outsiderCredentials!.email,
    outsiderCredentials!.password,
  );
  await expect(page).not.toHaveURL(/\/login/, { timeout: 30_000 });

  fs.mkdirSync(path.dirname(OUTSIDER_STORAGE_STATE), { recursive: true });
  await page.context().storageState({ path: OUTSIDER_STORAGE_STATE });
});
