import dotenv from "dotenv";
import path from "node:path";

// Loaded here rather than in playwright.config.ts: imports are hoisted, so the
// constants below would otherwise be evaluated before the .env file was read.
dotenv.config({ path: path.join(__dirname, "..", ".env") });

export const STORAGE_STATE = path.join(__dirname, "..", ".auth", "user.json");
export const OUTSIDER_STORAGE_STATE = path.join(
  __dirname,
  "..",
  ".auth",
  "outsider.json",
);

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
 * An optional second account that is signed in but has no access to the test
 * workspace: not a member of it, and not an admin or owner of its organization,
 * which would grant access to every workspace in it. The tests that need it
 * are skipped when it is not configured.
 */
export const outsiderCredentials =
  process.env.E2E_OUTSIDER_EMAIL && process.env.E2E_OUTSIDER_PASSWORD
    ? {
        email: process.env.E2E_OUTSIDER_EMAIL,
        password: process.env.E2E_OUTSIDER_PASSWORD,
      }
    : null;

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

/**
 * A dedicated, otherwise-empty workspace. The feature tests create and remove
 * their own resources inside it, so it is expected to be left empty.
 */
export const workspace = {
  slug: process.env.E2E_WORKSPACE_SLUG ?? "playwright-ws",
};

export const workspacePaths = {
  home: `/workspaces/${workspace.slug}/`,
  files: `/workspaces/${workspace.slug}/files/`,
  datasets: `/workspaces/${workspace.slug}/datasets/`,
  connections: `/workspaces/${workspace.slug}/connections/`,
  pipelines: `/workspaces/${workspace.slug}/pipelines/`,
  webapps: `/workspaces/${workspace.slug}/webapps/`,
  dataStudio: `/workspaces/${workspace.slug}/data-studio/`,
  savedQueries: `/workspaces/${workspace.slug}/data-studio/queries/`,
  settings: `/workspaces/${workspace.slug}/settings/`,
};

export const organizationPaths = {
  workspaces: `/organizations/${organization.id}/`,
  members: `/organizations/${organization.id}/members/`,
  externalCollaborators: `/organizations/${organization.id}/external-collaborators/`,
  datasets: `/organizations/${organization.id}/datasets/`,
  settings: `/organizations/${organization.id}/settings/`,
};
