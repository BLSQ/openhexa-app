import { Frame, Locator, Page } from "@playwright/test";

import { workspacePaths } from "../config/environment";

/** The JupyterHub page, which frames the user's server for the workspace. */
export class WorkspaceNotebooksPage {
  constructor(private readonly page: Page) {}

  async goto() {
    await this.page.goto(workspacePaths.home.replace(/\/$/, "/notebooks/"));
  }

  /** Points at the hub's /user/<user>/<workspace>/ once a server is assigned. */
  get serverFrame(): Locator {
    return this.page.getByRole("main").locator("iframe");
  }

  /** The framed JupyterLab, once the hub has redirected to it. */
  labFrame(): Frame | undefined {
    return this.page.frames().find((frame) => /\/lab\b/.test(frame.url()));
  }
}
