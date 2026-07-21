import { getCookie } from "cookies-next";
import { readFileSync } from "fs";
import { resolve } from "path";
import { downloadQueryCsv, SUCCESS_COOKIE_PREFIX } from "./downloadQueryCsv";

jest.mock("cookies-next", () => ({
  getCookie: jest.fn(),
}));

const DOWNLOAD_FRAME = 'iframe[name="data-studio-csv-download-frame"]';

// The download handshake spans two tiers with no shared code path; this single
// file (also read by the backend's test_views.py) is the one source of truth for
// the constants they must agree on. Reading it here binds the frontend to it.
const CONTRACT = JSON.parse(
  readFileSync(
    resolve(
      __dirname,
      "../../../../../backend/hexa/databases/tests/fixtures/download_contract.json",
    ),
    "utf-8",
  ),
);

const fieldValue = (form: HTMLFormElement, name: string) =>
  form.querySelector<HTMLInputElement>(`input[name="${name}"]`)?.value;

describe("downloadQueryCsv", () => {
  let submittedForms: HTMLFormElement[];
  let submitSpy: jest.SpyInstance;

  beforeEach(() => {
    jest.useFakeTimers();
    submittedForms = [];
    // jsdom does not implement form submission/navigation, so capture the form
    // at submit time instead of letting it navigate.
    submitSpy = jest
      .spyOn(HTMLFormElement.prototype, "submit")
      .mockImplementation(function (this: HTMLFormElement) {
        submittedForms.push(this);
      });
    (getCookie as jest.Mock).mockReturnValue("csrf-token-123");
    document.body.innerHTML = "";
  });

  afterEach(() => {
    submitSpy.mockRestore();
    jest.clearAllTimers();
    jest.useRealTimers();
  });

  it("posts the query, token and CSRF token to the download endpoint", () => {
    void downloadQueryCsv("ws-1", "SELECT 1");

    expect(submittedForms).toHaveLength(1);
    const form = submittedForms[0];
    expect(form.method).toBe("post");
    expect(form.getAttribute("action")).toContain(
      "/databases/ws-1/query/download/",
    );
    expect(form.target).toBe("data-studio-csv-download-frame");
    expect(fieldValue(form, "query")).toBe("SELECT 1");
    expect(fieldValue(form, "download_token")).toBeTruthy();
    expect(fieldValue(form, "csrfmiddlewaretoken")).toBe("csrf-token-123");
  });

  it("encodes the workspace slug into the URL", () => {
    void downloadQueryCsv("ws/odd slug", "SELECT 1");
    expect(submittedForms[0].getAttribute("action")).toContain(
      "/databases/ws%2Fodd%20slug/query/download/",
    );
  });

  it("reuses a single hidden download iframe across calls", () => {
    void downloadQueryCsv("ws-1", "SELECT 1");
    void downloadQueryCsv("ws-1", "SELECT 2");

    expect(document.querySelectorAll(DOWNLOAD_FRAME)).toHaveLength(1);
    expect(submittedForms).toHaveLength(2);
  });

  it("omits the CSRF field when there is no token cookie", () => {
    (getCookie as jest.Mock).mockReturnValue(undefined);
    void downloadQueryCsv("ws-1", "SELECT 1");
    expect(
      fieldValue(submittedForms[0], "csrfmiddlewaretoken"),
    ).toBeUndefined();
  });

  it("removes the transient form from the document after submitting", () => {
    void downloadQueryCsv("ws-1", "SELECT 1");
    expect(document.querySelectorAll("form")).toHaveLength(0);
  });

  it("resolves once the server sets the per-token cookie (download started)", async () => {
    // The backend sets a cookie named csvDownloadToken-<token> when streaming
    // begins; presence of that exact name is the "download began" signal.
    const cookies: Record<string, string> = {};
    (getCookie as jest.Mock).mockImplementation((name: string) =>
      name === "csrftoken" ? "csrf-token-123" : cookies[name],
    );

    const promise = downloadQueryCsv("ws-1", "SELECT 1");
    const token = fieldValue(submittedForms[0], "download_token");
    cookies[`${SUCCESS_COOKIE_PREFIX}${token}`] = "1";

    jest.advanceTimersByTime(300);
    await expect(promise).resolves.toBeUndefined();
  });

  it("waits on a per-call cookie so concurrent downloads do not clobber each other", async () => {
    const cookies: Record<string, string> = {};
    (getCookie as jest.Mock).mockImplementation((name: string) =>
      name === "csrftoken" ? "csrf-token-123" : cookies[name],
    );

    const first = downloadQueryCsv("ws-1", "SELECT 1");
    const second = downloadQueryCsv("ws-1", "SELECT 2");
    const tokenA = fieldValue(submittedForms[0], "download_token")!;
    const tokenB = fieldValue(submittedForms[1], "download_token")!;
    expect(tokenA).not.toBe(tokenB);

    // Only the second download's signal arrives; the first must keep waiting.
    cookies[`${SUCCESS_COOKIE_PREFIX}${tokenB}`] = "1";
    jest.advanceTimersByTime(300);
    await expect(second).resolves.toBeUndefined();

    // The first download settles on its own signal, unaffected by the second.
    cookies[`${SUCCESS_COOKIE_PREFIX}${tokenA}`] = "1";
    jest.advanceTimersByTime(300);
    await expect(first).resolves.toBeUndefined();
  });

  it("rejects with the server's message when an error page loads in the iframe", async () => {
    const promise = downloadQueryCsv("ws-1", "SELECT bad");
    const assertion = expect(promise).rejects.toThrow(
      "Only a single SQL statement",
    );

    const iframe = document.querySelector<HTMLIFrameElement>(DOWNLOAD_FRAME)!;
    // A failed response navigates the iframe to an error body (unlike a download).
    iframe.contentDocument!.body.textContent =
      "Only a single SQL statement can be executed.";
    iframe.dispatchEvent(new Event("load"));

    await assertion;
  });

  it("rejects when the download never starts (timeout)", async () => {
    (getCookie as jest.Mock).mockReturnValue(undefined);
    const promise = downloadQueryCsv("ws-1", "SELECT 1");
    const assertion = expect(promise).rejects.toThrow("timed out");

    jest.advanceTimersByTime(10 * 60 * 1000 + 1000);
    await assertion;
  });

  describe("stays in sync with the shared cross-tier contract", () => {
    // These bind the frontend implementation to download_contract.json, which the
    // backend view is asserted against too. If either tier renames one of these
    // constants without the other, the offending side's test fails here rather
    // than the handshake breaking silently in production (a download that appears
    // to hang until the client timeout).
    it("polls for the cookie name prefix the backend sets", () => {
      expect(SUCCESS_COOKIE_PREFIX).toBe(CONTRACT.cookiePrefix);
    });

    it("posts under the field names the backend reads", () => {
      void downloadQueryCsv("ws-1", "SELECT 1");
      const form = submittedForms[0];
      expect(fieldValue(form, CONTRACT.fields.query)).toBe("SELECT 1");
      expect(fieldValue(form, CONTRACT.fields.token)).toBeTruthy();
    });
  });
});
