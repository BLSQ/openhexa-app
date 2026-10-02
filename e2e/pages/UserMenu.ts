import { Locator, Page, expect } from "@playwright/test";

export type InterfaceLanguage = "English" | "Français";

/** The few labels the language test reads, as each language renders them. */
export const LABELS: Record<
  InterfaceLanguage,
  { accountSettings: string; yourAccount: string }
> = {
  English: { accountSettings: "Account settings", yourAccount: "Your account" },
  Français: {
    accountSettings: "Paramètres du compte",
    yourAccount: "Votre compte",
  },
};

/**
 * The menu behind the signed-in user's name, at the bottom of the sidebar. Its
 * labels are given in English: switch back before using it after a switch.
 */
export class UserMenu {
  constructor(
    private readonly page: Page,
    private readonly email: string,
  ) {}

  /** Named after the user's display name and email, both shown on it. */
  get button(): Locator {
    return this.page.getByRole("button", { name: this.email });
  }

  /** By its label, in whichever language the interface is in. */
  link(name: string): Locator {
    return this.page.getByRole("link", { name, exact: true });
  }

  get signOutButton(): Locator {
    return this.page.getByRole("button", { name: "Sign out" });
  }

  /** Its "Interface language" label is not tied to it, so the options find it. */
  get languageSelect(): Locator {
    return this.page
      .getByRole("combobox")
      .filter({ has: this.page.getByRole("option", { name: "Français" }) });
  }

  async open() {
    await this.button.click();
    await expect(this.languageSelect).toBeVisible();
  }

  /**
   * Saves the language on the account, then the app reloads at its root. It is
   * a setting of the user, not of the browser: every session of that account
   * follows it.
   */
  async switchLanguage(language: InterfaceLanguage) {
    await this.open();
    await this.languageSelect.selectOption({ label: language });
    await this.page.waitForURL(
      (url) => url.pathname === "/" || url.pathname.startsWith("/workspaces/"),
    );
    await this.page.waitForLoadState("networkidle");
  }

  /**
   * Puts the account back in English through the API, so a test that failed
   * while in French does not leave the next run reading French labels.
   */
  async resetLanguageToEnglish() {
    await this.page.goto("/");
    const response = await this.page.evaluate(async () => {
      const csrf = document.cookie.match(/csrftoken=([^;]+)/)?.[1] ?? "";
      const res = await fetch("/graphql/", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
        body: JSON.stringify({
          query: `mutation { updateUser(input: { language: "en" }) { success errors } }`,
        }),
      });
      return res.json();
    });
    expect(response?.data?.updateUser?.success, JSON.stringify(response)).toBe(
      true,
    );
  }
}
