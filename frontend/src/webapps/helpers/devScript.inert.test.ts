/**
 * @jest-environment-options {"url": "https://my-app.webapps.example.com/"}
 */
import fs from "fs";
import path from "path";

// On a non-local host (the deployed webapp), dev.js must be completely inert:
// no popup, no fetch override, no pill, and window.OPENHEXA left untouched.
const DEV_JS_PATH = path.resolve(
  __dirname,
  "../../../../backend/hexa/templates/webapps/dev.js",
);

function loadDevScript() {
  const src = fs
    .readFileSync(DEV_JS_PATH, "utf8")
    .replace("{{ base_url|escapejs }}", "https://openhexa.test");
  (0, eval)(src);
}

describe("webapps dev.js — inert on non-local hosts", () => {
  it("does nothing when the page is served from a real webapp host", () => {
    (window as any).__OPENHEXA_DEV_ACTIVE__ = undefined;
    (window as any).OPENHEXA = undefined;
    (window as any).OPENHEXA_DEV = {
      workspaceSlug: "my-ws",
      webappSlug: "my-app",
    };
    const openMock = jest.fn();
    (window as any).open = openMock;
    const originalFetch = jest.fn();
    (window as any).fetch = originalFetch;

    loadDevScript();

    expect(openMock).not.toHaveBeenCalled();
    expect((window as any).fetch).toBe(originalFetch); // fetch not wrapped
    expect((window as any).OPENHEXA).toBeUndefined();
    expect(document.body.textContent).toBe("");
  });
});
