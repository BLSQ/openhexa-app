import { credentials, outsiderCredentials } from "../config/environment";
import { expect, test } from "../fixtures/visitors";
import { uniqueName } from "../helpers/confirm";
import { ServedWebapp, staticAppHtml } from "../pages/ServedWebapp";
import { ICON_PNG, WorkspaceWebappsPage } from "../pages/WorkspaceWebappsPage";

/** What a new static app is created with, from the default template. */
const TEMPLATE_HEADING = "Hello World";

test.describe("Workspace static web apps", () => {
  test("a static web app is edited, versioned, renamed and deleted", async ({
    page,
    cleanup,
  }) => {
    test.setTimeout(180_000);
    const webapps = new WorkspaceWebappsPage(page);
    const served = new ServedWebapp(await page.context().newPage());
    const name = uniqueName("e2e static");
    const marker = uniqueName("E2E-EDITED");

    const slug = await webapps.create("Static", name);
    cleanup.add(`web app ${slug}`, () => webapps.deleteIfPresent(slug));
    let url = "";

    await test.step("it is listed, private, with every tab", async () => {
      await webapps.goto();
      await expect(webapps.row(name)).toBeVisible();
      await expect(webapps.rowAccess(name, "Private")).toBeVisible();

      await webapps.gotoTab(slug, "General");
      for (const tab of ["General", "Code", "History", "API access"] as const) {
        await expect(webapps.tab(tab)).toBeVisible();
      }
      url = (await webapps.publishedUrl.getAttribute("href"))!;
    });

    await test.step("it serves the template", async () => {
      await served.goto(url);
      await expect(served.heading(TEMPLATE_HEADING)).toBeVisible();
    });

    await test.step("editing the code publishes it", async () => {
      await webapps.editCode(slug, staticAppHtml(marker));
      await served.goto(url);
      await expect(served.heading(marker)).toBeVisible();
    });

    await test.step("history lists both commits and their diffs", async () => {
      await webapps.gotoTab(slug, "History");
      await expect(webapps.commitLink("Initial content")).toBeVisible();
      await expect(webapps.commitTitle("Update webapp content")).toContainText(
        "Published",
      );
      await expect(webapps.commitTitle("Initial content")).not.toContainText(
        "Published",
      );

      await webapps.commitLink("Update webapp content").click();
      await expect(webapps.diffLine(marker)).toBeVisible();
      await webapps.backToHistory.click();
      await expect(webapps.commitLink("Initial content")).toBeVisible();
    });

    await test.step("publishing the first commit rolls it back", async () => {
      const initial = await webapps.commitId("Initial content");
      await webapps.publishVersion(slug, initial);

      await served.goto(url);
      await expect(served.heading(TEMPLATE_HEADING)).toBeVisible();

      await webapps.gotoTab(slug, "History");
      await expect(webapps.commitTitle("Initial content")).toContainText(
        "Published",
      );
      await expect(
        webapps.commitTitle("Update webapp content"),
      ).not.toContainText("Published");
    });

    const renamed = uniqueName("e2e renamed");
    const subdomain = uniqueName("e2e-sub").toLowerCase();

    await test.step("its name, subdomain and icon change", async () => {
      await webapps.gotoTab(slug, "General");
      await webapps.updateDetails({
        name: renamed,
        subdomain,
        icon: ICON_PNG,
      });
      await expect(webapps.publishedUrl).toContainText(`//${subdomain}.`);

      const previousUrl = url;
      url = (await webapps.publishedUrl.getAttribute("href"))!;
      await served.goto(url);
      await expect(served.heading(TEMPLATE_HEADING)).toBeVisible();
      const response = await served.goto(previousUrl);
      expect(response?.status()).toBe(404);

      await webapps.goto();
      await expect(webapps.row(renamed)).toBeVisible();
      await expect(webapps.rowIcon(renamed)).toBeVisible();
      await expect(webapps.row(name)).toHaveCount(0);
    });

    await test.step("deleting it takes it offline", async () => {
      await webapps.gotoWebapp(slug);
      await webapps.delete();
      await expect(webapps.row(renamed)).toHaveCount(0);

      const response = await served.goto(url);
      expect(response?.status()).toBe(404);
    });
  });

  test("a private app needs a sign-in and API access; a public one neither", async ({
    page,
    anonymousPage,
    cleanup,
  }) => {
    test.setTimeout(180_000);
    const webapps = new WorkspaceWebappsPage(page);
    const member = new ServedWebapp(await page.context().newPage());
    const anonymous = new ServedWebapp(anonymousPage);
    const name = uniqueName("e2e access");
    const marker = uniqueName("E2E-ACCESS");

    const slug = await webapps.create("Static", name);
    cleanup.add(`web app ${slug}`, () => webapps.deleteIfPresent(slug));
    await webapps.editCode(slug, staticAppHtml(marker));
    const url = await webapps.servedUrl(slug);

    await test.step("a private app sends visitors to sign in", async () => {
      await anonymous.goto(url);
      await expect(anonymousPage).toHaveURL(/\/login/);
      await expect(anonymous.loginHeading).toBeVisible();
    });

    await test.step("a member sees it, but not the API by default", async () => {
      await member.goto(url);
      await expect(member.heading(marker)).toBeVisible();
      await expect(member.apiResult).toHaveText(
        "API error 403: Operations not allowed: me",
      );
    });

    await test.step("enabling a scope opens that part of the API", async () => {
      await webapps.enableApiScope(slug, "Read user info");
      await webapps.gotoTab(slug, "API access");
      await expect(webapps.apiScope("Read user info")).toBeChecked();
      await expect(webapps.apiScope("Read datasets")).not.toBeChecked();

      await member.goto(url);
      await expect(member.apiResult).toHaveText(
        `API user: ${credentials.email}`,
      );
    });

    await test.step("a public app has no API access to configure", async () => {
      await webapps.gotoTab(slug, "General");
      await webapps.updateDetails({ isPublic: true });

      await webapps.gotoTab(slug, "General");
      await expect(webapps.tab("Code")).toBeVisible();
      await expect(webapps.tab("API access")).toHaveCount(0);

      await webapps.gotoTab(slug, "API access");
      await page.waitForLoadState("networkidle");
      await expect(webapps.apiScope("Read user info")).toHaveCount(0);

      await webapps.goto();
      await expect(webapps.rowAccess(name, "Public")).toBeVisible();
    });

    await test.step("anyone sees a public app, without the API", async () => {
      await anonymous.goto(url);
      await expect(anonymous.heading(marker)).toBeVisible();
      await expect(anonymous.poweredByBanner).toBeVisible();
      await expect(anonymous.apiResult).toHaveText(
        "API error 404: Not available",
      );

      await member.goto(url);
      await expect(member.heading(marker)).toBeVisible();
      await expect(member.poweredByBanner).toHaveCount(0);
      await expect(member.apiResult).toHaveText("API error 404: Not available");
    });

    await test.step("a private app again sends visitors to sign in", async () => {
      await webapps.gotoTab(slug, "General");
      await webapps.updateDetails({ isPublic: false });

      await anonymous.goto(url);
      await expect(anonymous.loginHeading).toBeVisible();
      await webapps.gotoTab(slug, "General");
      await expect(webapps.tab("API access")).toBeVisible();
    });
  });

  test.describe("seen from outside the workspace", () => {
    test.skip(
      !outsiderCredentials,
      "Needs E2E_OUTSIDER_EMAIL / E2E_OUTSIDER_PASSWORD for an account outside the test workspace",
    );

    test("a private app is forbidden, a public one is served", async ({
      page,
      outsiderPage,
      cleanup,
    }) => {
      const webapps = new WorkspaceWebappsPage(page);
      const outsider = new ServedWebapp(outsiderPage);
      const name = uniqueName("e2e outsider");

      const slug = await webapps.create("Static", name);
      cleanup.add(`web app ${slug}`, () => webapps.deleteIfPresent(slug));
      const url = await webapps.servedUrl(slug);

      await outsider.goto(url);
      await expect(outsider.forbidden).toBeVisible();
      await expect(outsider.heading(TEMPLATE_HEADING)).toHaveCount(0);

      await webapps.updateDetails({ isPublic: true });
      await outsider.goto(url);
      await expect(outsider.heading(TEMPLATE_HEADING)).toBeVisible();
    });
  });
});
