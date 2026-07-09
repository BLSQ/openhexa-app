import { getDefaultHtmlTemplate } from "./templates";

describe("getDefaultHtmlTemplate", () => {
  afterEach(() => {
    delete (window as any).__ENV__;
  });

  it("includes the dev.js script tag pointing at the configured backend URL", () => {
    (window as any).__ENV__ = {
      OPENHEXA_BACKEND_URL: "https://app.openhexa.test",
    };

    const html = getDefaultHtmlTemplate();

    expect(html).toContain(
      '<script src="https://app.openhexa.test/webapps/dev.js"></script>',
    );
    expect(html).toContain("<title>My Webapp</title>");
    expect(html).toContain("Hello World");
  });
});
