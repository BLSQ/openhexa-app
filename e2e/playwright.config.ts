import { defineConfig, devices } from "@playwright/test";

import { BASE_URL, STORAGE_STATE } from "./config/environment";

const isCI = !!process.env.CI;

export default defineConfig({
  testDir: "./tests",
  // The suite runs against a shared, deployed environment, so every wait is a
  // network wait: be more patient than the local-server defaults.
  timeout: 60_000,
  expect: { timeout: 15_000 },
  fullyParallel: true,
  forbidOnly: isCI,
  retries: isCI ? 2 : 0,
  // A single account on a shared environment; keep the load modest.
  workers: isCI ? 2 : undefined,
  reporter: isCI
    ? [["github"], ["html", { open: "never" }], ["list"]]
    : [["html", { open: "never" }], ["list"]],
  use: {
    baseURL: BASE_URL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    actionTimeout: 15_000,
    navigationTimeout: 30_000,
    // Headed runs are otherwise too fast to follow; `npm run test:watch` sets
    // this so each action is visible.
    launchOptions: {
      slowMo: Number(process.env.E2E_SLOW_MO ?? 0),
    },
  },
  projects: [
    {
      name: "setup",
      testDir: "./fixtures",
      testMatch: /auth\.setup\.ts/,
    },
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        storageState: STORAGE_STATE,
        // Taller than the Desktop Chrome default, which this must come after to
        // override: several create dialogs put their actions below the fold at
        // 720px, where Playwright will not click them.
        viewport: { width: 1440, height: 1080 },
      },
      dependencies: ["setup"],
    },
  ],
});
