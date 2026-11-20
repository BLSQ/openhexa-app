import { mailgun } from "../config/environment";
import { Mailbox } from "../helpers/mailbox";
import { test as base } from "./cleanup";

/**
 * The suite's mailbox, opened for the test and closed after it. A test that
 * asks for it is skipped when `E2E_MAILGUN_API_KEY` is not set; see `mailgun`
 * in `config/environment.ts`.
 */
export const test = base.extend<{ mailbox: Mailbox }>({
  mailbox: async ({}, use) => {
    // Here rather than in the test body, which only runs once this has opened.
    base.skip(
      !mailgun,
      "Needs E2E_MAILGUN_API_KEY for a mailbox the suite can read",
    );
    const mailbox = await Mailbox.open();
    await use(mailbox);
    await mailbox.dispose();
  },
});

export { expect } from "@playwright/test";
