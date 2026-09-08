import { expect, test } from "@playwright/test";

import { organization, organizationPaths } from "../config/environment";
import {
  OrganizationSection,
  OrganizationSidebar,
} from "../pages/OrganizationSidebar";

type SectionExpectation = {
  section: OrganizationSection;
  path: string;
  title: string;
  /** Something rendered inside <main> that only this section renders. */
  anchor: (
    page: import("@playwright/test").Page,
  ) => import("@playwright/test").Locator;
};

const sections: SectionExpectation[] = [
  {
    section: "Workspaces",
    path: organizationPaths.workspaces,
    title: "OpenHEXA | Organization",
    anchor: (page) => page.getByPlaceholder("Search workspaces..."),
  },
  {
    section: "Members",
    path: organizationPaths.members,
    title: "OpenHEXA | Members",
    anchor: (page) => page.getByPlaceholder("Search members..."),
  },
  {
    section: "External Collaborators",
    path: organizationPaths.externalCollaborators,
    title: "OpenHEXA | External Collaborators",
    anchor: (page) =>
      page.getByRole("heading", {
        name: "Pending Direct Workspace Invitations",
      }),
  },
  {
    section: "Datasets",
    path: organizationPaths.datasets,
    title: "OpenHEXA | Datasets",
    anchor: (page) =>
      page.getByRole("columnheader", { name: "Source workspace" }),
  },
  {
    section: "Settings",
    path: organizationPaths.settings,
    title: "OpenHEXA | Settings",
    anchor: (page) =>
      page.getByRole("heading", { name: "Organization Settings", level: 1 }),
  },
];

test.describe("Organization navigation", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(organizationPaths.workspaces);
  });

  test("the sidebar offers every organization section", async ({ page }) => {
    const sidebar = new OrganizationSidebar(page);

    await expect(
      sidebar.organizationLink(organization.shortName),
    ).toBeVisible();
    for (const { section, path } of sections) {
      await expect(sidebar.link(section)).toHaveAttribute("href", path);
    }
    await expect(sidebar.userMenuButton).toBeVisible();
  });

  for (const { section, path, title, anchor } of sections) {
    test(`the sidebar opens ${section}`, async ({ page }) => {
      const sidebar = new OrganizationSidebar(page);

      await sidebar.open(section);

      await expect(page).toHaveURL(new RegExp(`${path}$`));
      await expect(page).toHaveTitle(title);
      await expect(anchor(page)).toBeVisible();
      // The layout must survive the transition: a client-side navigation that
      // drops the sidebar is exactly the regression this guards.
      await expect(sidebar.link(section)).toBeVisible();
    });
  }

  for (const { section, path, title, anchor } of sections) {
    test(`${section} is reachable by direct link`, async ({ page }) => {
      await page.goto(path);

      await expect(page).toHaveTitle(title);
      await expect(anchor(page)).toBeVisible();
    });
  }

  test("an unknown organization id is a 404", async ({ page }) => {
    const response = await page.goto(
      "/organizations/00000000-0000-4000-8000-000000000000/",
    );

    expect(response?.status()).toBe(404);
  });
});
