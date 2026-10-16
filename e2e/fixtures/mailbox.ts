import { Mailbox } from "../helpers/mailbox";
import { test as base } from "./cleanup";

/**
 * The suite's mailbox, opened for the test and closed after it. Specs that use
 * it skip themselves when `E2E_MAILGUN_API_KEY` is not set; see `mailgun` in
 * `config/environment.ts`.
 */
export const test = base.extend<{ mailbox: Mailbox }>({
  mailbox: async ({}, use) => {
    const mailbox = await Mailbox.open();
    await use(mailbox);
    await mailbox.dispose();
  },
});

export { expect } from "@playwright/test";
