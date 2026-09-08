import dotenv from "dotenv";
import path from "node:path";

// Loaded here rather than in playwright.config.ts: imports are hoisted, so the
// constants below would otherwise be evaluated before the .env file was read.
dotenv.config({ path: path.join(__dirname, "..", ".env") });

export const STORAGE_STATE = path.join(__dirname, "..", ".auth", "user.json");

export const BASE_URL =
  process.env.E2E_BASE_URL ?? "https://app.demo.openhexa.org";

function required(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(
      `Missing ${name}. Copy e2e/.env.example to e2e/.env and fill it in, or export it in your shell.`,
    );
  }
  return value;
}

export const credentials = {
  get email() {
    return required("E2E_EMAIL");
  },
  get password() {
    return required("E2E_PASSWORD");
  },
};

/**
 * The organization the suite navigates. It is a dedicated, otherwise-unused
 * organization on the target environment, so its name and short name are stable
 * enough to assert on.
 */
export const organization = {
  id: process.env.E2E_ORGANIZATION_ID ?? "9c0eda6f-5450-4167-be64-e4decbf4da46",
  name: process.env.E2E_ORGANIZATION_NAME ?? "Playwright Integration Testing",
  shortName: process.env.E2E_ORGANIZATION_SHORT_NAME ?? "PIT",
};

export const organizationPaths = {
  workspaces: `/organizations/${organization.id}/`,
  members: `/organizations/${organization.id}/members/`,
  externalCollaborators: `/organizations/${organization.id}/external-collaborators/`,
  datasets: `/organizations/${organization.id}/datasets/`,
  settings: `/organizations/${organization.id}/settings/`,
};
