import fs from "fs";
import path from "path";

// dev.js is a backend template served at /webapps/dev.js. We load the real
// file (substituting the Django `base_url` placeholder) and exercise it in
// jsdom so the local-dev handshake contract can't regress silently.
const DEV_JS_PATH = path.resolve(
  __dirname,
  "../../../../backend/hexa/templates/webapps/dev.js",
);
const BASE = "https://openhexa.test";

function loadDevScript() {
  const src = fs
    .readFileSync(DEV_JS_PATH, "utf8")
    .replace("{{ base_url|escapejs }}", BASE);
  // Indirect eval runs in global scope so the IIFE's `window`/`document`
  // references resolve to the jsdom globals.
  (0, eval)(src);
}

function findButton(label: string): HTMLButtonElement | undefined {
  return Array.from(document.querySelectorAll("button")).find(
    (b) => b.textContent === label,
  ) as HTMLButtonElement | undefined;
}

function completeHandshake(overrides: Record<string, unknown> = {}) {
  window.dispatchEvent(
    new MessageEvent("message", {
      origin: BASE,
      data: {
        type: "openhexa-dev-auth",
        previewUrl: "https://key123.webapps.test/",
        workspaceSlug: "my-ws",
        webappSlug: "my-app",
        ...overrides,
      },
    }),
  );
}

function connect(overrides: Record<string, unknown> = {}) {
  findButton("Connect to OpenHEXA")!.click();
  completeHandshake(overrides);
}

describe("webapps dev.js — local development shim", () => {
  let openMock: jest.Mock;
  let fetchMock: jest.Mock;
  let messageListeners: EventListener[] = [];

  beforeEach(() => {
    // dev.js attaches a persistent window "message" listener on each eval;
    // drop the ones left by previous tests so a handshake only reaches the
    // listener from the current test's eval.
    messageListeners.forEach((l) => window.removeEventListener("message", l));
    messageListeners = [];
    const realAddEventListener = window.addEventListener.bind(window);
    jest
      .spyOn(window, "addEventListener")
      .mockImplementation((type, listener, options) => {
        if (type === "message" && typeof listener === "function") {
          messageListeners.push(listener as EventListener);
        }
        realAddEventListener(type as any, listener as any, options as any);
      });

    jest.spyOn(console, "info").mockImplementation(() => {});
    document.body.innerHTML = "";
    (window as any).__OPENHEXA_DEV_ACTIVE__ = undefined;
    (window as any).OPENHEXA = undefined;
    (window as any).OPENHEXA_DEV = {
      workspaceSlug: "my-ws",
      webappSlug: "my-app",
    };
    sessionStorage.clear();
    openMock = jest.fn(() => ({ close: jest.fn() }));
    (window as any).open = openMock;
    fetchMock = jest.fn(() =>
      Promise.resolve({ status: 200, json: async () => ({}) }),
    );
    (window as any).fetch = fetchMock;
  });

  it("shows a Connect button and only opens the handshake on click", () => {
    loadDevScript();
    expect(openMock).not.toHaveBeenCalled();
    const btn = findButton("Connect to OpenHEXA");
    expect(btn).toBeTruthy();

    btn!.click();

    expect(openMock).toHaveBeenCalledTimes(1);
    const url = openMock.mock.calls[0][0] as string;
    expect(url).toContain(`${BASE}/webapps/dev-auth/`);
    expect(url).toContain("workspaceSlug=my-ws");
    expect(url).toContain("webappSlug=my-app");
    expect(url).toContain("origin=");
  });

  it("never opens a popup for a /graphql/ call made before the user connects", () => {
    loadDevScript();
    // A page that fetches on load must not trigger a popup; the call just pends.
    void (window as any).fetch("/graphql/", { method: "POST", body: "{}" });
    expect(openMock).not.toHaveBeenCalled();
  });

  it("omits the target params when workspace/webapp aren't both set (picker mode)", () => {
    (window as any).OPENHEXA_DEV = {};
    loadDevScript();
    findButton("Connect to OpenHEXA")!.click();
    const url = openMock.mock.calls[0][0] as string;
    expect(url).not.toContain("workspaceSlug=");
    expect(url).not.toContain("webappSlug=");
  });

  it("sets window.OPENHEXA and shows a pill with both slugs after the handshake", () => {
    loadDevScript();
    connect();
    expect((window as any).OPENHEXA).toEqual({
      workspaceSlug: "my-ws",
      webappSlug: "my-app",
      isPublic: false,
    });
    const pill = document.body.textContent ?? "";
    expect(pill).toContain("my-ws");
    expect(pill).toContain("my-app");
  });

  it("reroutes /graphql/ to the preview endpoint with credentials omitted", async () => {
    loadDevScript();
    connect();
    fetchMock.mockClear();

    await (window as any).fetch("/graphql/", {
      method: "POST",
      body: JSON.stringify({ query: "{ me { user { email } } }" }),
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [target, init] = fetchMock.mock.calls[0];
    expect(target).toBe("https://key123.webapps.test/graphql/");
    expect(init.credentials).toBe("omit");
  });

  it("does not touch non-/graphql/ fetches", async () => {
    loadDevScript();
    fetchMock.mockClear();

    await (window as any).fetch("/data/file.csv");

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0][0]).toBe("/data/file.csv");
  });

  it("reuses the cached credential on reload without opening a popup", () => {
    loadDevScript();
    connect();

    // Simulate a page refresh in the same tab: fresh eval, same sessionStorage.
    (window as any).__OPENHEXA_DEV_ACTIVE__ = undefined;
    (window as any).OPENHEXA = undefined;
    openMock.mockClear();

    loadDevScript();

    expect(openMock).not.toHaveBeenCalled();
    expect((window as any).OPENHEXA.webappSlug).toBe("my-app");
  });

  it("reloads the page (rather than re-rendering the pill) when switching web app", () => {
    // jsdom's reload() is an unimplemented no-op that logs to console.error;
    // assert the observable effect: on a switch the pill is NOT re-rendered in
    // place (a broken reload would swap it to the new app instead).
    jest.spyOn(console, "error").mockImplementation(() => {});
    (window as any).OPENHEXA_DEV = {}; // picker mode → pill shows "Switch"

    loadDevScript();
    connect({ workspaceSlug: "ws-a", webappSlug: "app-a" });
    expect(document.body.textContent).toContain("app-a");

    findButton("Switch")!.click();
    completeHandshake({ workspaceSlug: "ws-b", webappSlug: "app-b" });

    expect(document.body.textContent).toContain("app-a");
    expect(document.body.textContent).not.toContain("app-b");
  });

  it("prompts to reconnect and retries when the credential has expired", async () => {
    loadDevScript();
    connect();
    // The connection cached a credential.
    expect(sessionStorage.getItem("openhexa_dev:my-ws/my-app")).not.toBeNull();
    fetchMock.mockClear();

    // The first rerouted call hits an expired credential (404); the retry
    // (after reconnecting) succeeds with the default 200.
    fetchMock.mockResolvedValueOnce({ status: 404, json: async () => ({}) });

    const call = (window as any).fetch("/graphql/", {
      method: "POST",
      body: "{}",
    });

    // Let the 404 response be handled.
    await new Promise((resolve) => setTimeout(resolve, 0));

    // The stale credential is dropped and the Connect button is shown again...
    expect(sessionStorage.getItem("openhexa_dev:my-ws/my-app")).toBeNull();
    expect(findButton("Connect to OpenHEXA")).toBeTruthy();

    // ...and the original call stays pending until the user reconnects.
    findButton("Connect to OpenHEXA")!.click();
    completeHandshake();

    const res = await call;
    expect(res.status).toBe(200);
    // Expired attempt + successful retry, nothing more.
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});
