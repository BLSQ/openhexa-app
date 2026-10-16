import { APIRequestContext, request } from "@playwright/test";

import { mailgun } from "../config/environment";
import { uniqueName } from "./confirm";

/** An email as the suite reads it back: the stored message, lightly parsed. */
export type Email = {
  subject: string;
  from: string;
  to: string;
  /** The plain-text body, where the links are easiest to find. */
  text: string;
  html: string;
  receivedAt: Date;
  /** Every absolute URL in the plain-text body, in order. */
  links: URL[];
  /** Mailgun's handle on the stored message. */
  storageKey: string;
};

/** How long an email gets to arrive. Delivery takes seconds; the events API can lag a little more. */
const DEFAULT_TIMEOUT = 120_000;
const POLL_INTERVAL = 3_000;
/** Mailgun's clock and this machine's may disagree by a few seconds. */
const CLOCK_SKEW = 10_000;

/** An address of this run's own on the mailbox domain, so parallel tests never share an inbox. */
export function mailboxAddress(prefix: string): string {
  if (!mailgun) {
    throw new Error("E2E_MAILGUN_API_KEY is not set: no mailbox the suite can read");
  }
  return `${uniqueName(prefix)}@${mailgun.domain}`;
}

/**
 * The mailbox behind `*@<mailbox domain>`: a Mailgun receiving domain whose
 * route stores every message, read back over Mailgun's HTTP API. Nothing is
 * ever deleted; Mailgun drops stored messages after a few days by itself.
 *
 * Every lookup is bounded by an address and a start time, so a test only ever
 * sees the mail its own actions produced, and a second code or a resent
 * invitation is told apart from the first.
 */
export class Mailbox {
  /** Storage keys `waitForEmail` has already handed out. */
  private readonly delivered = new Set<string>();

  private constructor(
    private readonly api: APIRequestContext,
    private readonly domain: string,
  ) {}

  static async open(): Promise<Mailbox> {
    if (!mailgun) {
      throw new Error("E2E_MAILGUN_API_KEY is not set: no mailbox the suite can read");
    }
    const api = await request.newContext({
      baseURL: mailgun.apiBase,
      httpCredentials: { username: "api", password: mailgun.apiKey },
      storageState: { cookies: [], origins: [] },
    });
    return new Mailbox(api, mailgun.domain);
  }

  /** Every email stored for this address since then, oldest first. */
  async emailsSince(to: string, since: Date): Promise<Email[]> {
    // A stored event carries the envelope recipients, not the `recipient`
    // field the delivery events are filtered on.
    const response = await this.api.get(`/v3/${this.domain}/events`, {
      params: {
        event: "stored",
        recipients: to,
        begin: Math.floor((since.getTime() - CLOCK_SKEW) / 1000),
        ascending: "yes",
        limit: 50,
      },
    });
    if (!response.ok()) {
      throw new Error(
        `Mailgun refused the events query (${response.status()}): ${await response.text()}`,
      );
    }
    const { items } = (await response.json()) as {
      items: {
        timestamp: number;
        storage: { key: string };
        message: { recipients: string[] };
      }[];
    };
    const emails: Email[] = [];
    for (const item of items) {
      const receivedAt = new Date(item.timestamp * 1000);
      // The filter is a text match; keep only mail addressed to this inbox.
      if (
        receivedAt.getTime() < since.getTime() - CLOCK_SKEW ||
        !item.message.recipients.includes(to)
      ) {
        continue;
      }
      emails.push(await this.fetch(item.storage.key, receivedAt));
    }
    return emails;
  }

  /**
   * Waits for an email to this address, sent after `since`, with a matching
   * subject if one is given, and returns the first that qualifies. An email
   * is handed out once: the start time has a margin for clock skew, so a
   * second code or a resent invitation requested right after the first is
   * told apart from it. On timeout it names the subjects that did arrive, so
   * a failure reads like a finding.
   */
  async waitForEmail(
    to: string,
    { subject, since }: { subject?: string | RegExp; since: Date },
    { timeout = DEFAULT_TIMEOUT }: { timeout?: number } = {},
  ): Promise<Email> {
    const deadline = Date.now() + timeout;
    let seen: Email[] = [];
    while (Date.now() < deadline) {
      seen = (await this.emailsSince(to, since)).filter(
        (email) => !this.delivered.has(email.storageKey),
      );
      const match = seen.find((email) => matches(email.subject, subject));
      if (match) {
        this.delivered.add(match.storageKey);
        return match;
      }
      await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL));
    }
    const others = seen.length
      ? ` Other mail for it since then: ${seen.map((e) => JSON.stringify(e.subject)).join(", ")}.`
      : " Nothing arrived for it since then.";
    throw new Error(
      `No email ${subject ? `with subject ${subject} ` : ""}reached ${to} within ${timeout / 1000}s.${others}`,
    );
  }

  private async fetch(storageKey: string, receivedAt: Date): Promise<Email> {
    const response = await this.api.get(
      `/v3/domains/${this.domain}/messages/${storageKey}`,
      { headers: { Accept: "application/json" } },
    );
    if (!response.ok()) {
      throw new Error(
        `Mailgun refused the stored message (${response.status()}): ${await response.text()}`,
      );
    }
    const message = await response.json();
    const text: string = message["body-plain"] ?? "";
    return {
      subject: message.subject ?? "",
      from: message.from ?? message.sender ?? "",
      to: message.recipients ?? "",
      text,
      html: message["body-html"] ?? "",
      receivedAt,
      links: linksIn(text),
      storageKey,
    };
  }

  async dispose() {
    await this.api.dispose();
  }
}

function matches(subject: string, expected?: string | RegExp): boolean {
  if (expected === undefined) {
    return true;
  }
  return typeof expected === "string"
    ? subject === expected
    : expected.test(subject);
}

function linksIn(text: string): URL[] {
  const links: URL[] = [];
  for (const match of text.matchAll(/https?:\/\/[^\s<>"')\]]+/g)) {
    try {
      // A sentence may end right after the link.
      links.push(new URL(match[0].replace(/[.,;:!?]+$/, "")));
    } catch {
      // Not a URL after all; the next one may be.
    }
  }
  return links;
}

/** The first link whose path matches, e.g. `/register` or `/auth/reset/`. */
export function linkTo(email: Email, path: string | RegExp): URL {
  const link = email.links.find((url) =>
    typeof path === "string"
      ? url.pathname.startsWith(path)
      : path.test(url.pathname),
  );
  if (!link) {
    throw new Error(
      `No link to ${path} in the email "${email.subject}". Links: ${email.links.map(String).join(", ") || "none"}`,
    );
  }
  return link;
}

/** The one-time code in a two-factor email: "Enter this OTP code to verify your account: 123456". */
export function otpCode(email: Email): string {
  const match = email.text.match(/\b(\d{6})\b/);
  if (!match) {
    throw new Error(`No six-digit code in the email "${email.subject}": ${email.text}`);
  }
  return match[1];
}
