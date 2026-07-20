import { getCookie } from "cookies-next";
import { downloadQueryCsv } from "./downloadQueryCsv";

jest.mock("cookies-next", () => ({
  getCookie: jest.fn(),
}));

const DOWNLOAD_FRAME = 'iframe[name="data-studio-csv-download-frame"]';

const fieldValue = (form: HTMLFormElement, name: string) =>
  form.querySelector<HTMLInputElement>(`input[name="${name}"]`)?.value;

describe("downloadQueryCsv", () => {
  let submittedForms: HTMLFormElement[];
  let submitSpy: jest.SpyInstance;

  beforeEach(() => {
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
  });

  it("posts the query and CSRF token to the download endpoint", () => {
    downloadQueryCsv("ws-1", "SELECT 1");

    expect(submittedForms).toHaveLength(1);
    const form = submittedForms[0];
    expect(form.method).toBe("post");
    expect(form.getAttribute("action")).toContain(
      "/databases/ws-1/query/download/",
    );
    expect(form.target).toBe("data-studio-csv-download-frame");
    expect(fieldValue(form, "query")).toBe("SELECT 1");
    expect(fieldValue(form, "csrfmiddlewaretoken")).toBe("csrf-token-123");
  });

  it("encodes the workspace slug into the URL", () => {
    downloadQueryCsv("ws/odd slug", "SELECT 1");
    expect(submittedForms[0].getAttribute("action")).toContain(
      "/databases/ws%2Fodd%20slug/query/download/",
    );
  });

  it("reuses a single hidden download iframe across calls", () => {
    downloadQueryCsv("ws-1", "SELECT 1");
    downloadQueryCsv("ws-1", "SELECT 2");

    expect(document.querySelectorAll(DOWNLOAD_FRAME)).toHaveLength(1);
    expect(submittedForms).toHaveLength(2);
  });

  it("omits the CSRF field when there is no token cookie", () => {
    (getCookie as jest.Mock).mockReturnValue(undefined);
    downloadQueryCsv("ws-1", "SELECT 1");
    expect(
      fieldValue(submittedForms[0], "csrfmiddlewaretoken"),
    ).toBeUndefined();
  });

  it("removes the transient form from the document after submitting", () => {
    downloadQueryCsv("ws-1", "SELECT 1");
    expect(document.querySelectorAll("form")).toHaveLength(0);
  });
});
