import { test } from "@playwright/test";

import { features } from "../config/environment";

export type Feature = keyof typeof features;

const WITHOUT: Record<Feature, string> = {
  selfRegistration:
    "E2E_SERVER_CONFIGURATION_SELF_REGISTRATION_ENABLED=false: no self sign-up here.",
  ai: "E2E_SERVER_CONFIGURATION_AI_ENABLED=false: the assistant is not enabled here.",
  subscription:
    "E2E_SERVER_CONFIGURATION_SUBSCRIPTION_CONSOLE_ENABLED=false: no subscription console here.",
};

/**
 * Skips the running test, or every test of the `describe` it is called in,
 * when the environment is declared not to have one of the features. Nothing is
 * detected: an environment declared to have a feature fails without it.
 */
export function requires(...names: Feature[]) {
  const missing = names.filter((name) => !features[name]);
  test.skip(
    missing.length > 0,
    missing.map((name) => WITHOUT[name]).join(" "),
  );
}
