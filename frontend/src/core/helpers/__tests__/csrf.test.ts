import { getCsrfToken } from "../csrf";

describe("getCsrfToken", () => {
  afterEach(() => {
    delete window.__ENV__;
    document.cookie = "csrftoken=; Max-Age=0; path=/";
    document.cookie = "csrftoken_demo=; Max-Age=0; path=/";
  });

  it("reads the default cookie", () => {
    document.cookie = "csrftoken=default-token; path=/";

    expect(getCsrfToken()).toBe("default-token");
  });

  it("reads the cookie named by the runtime env, ignoring other environments' cookie", () => {
    window.__ENV__ = {
      CSRF_COOKIE_NAME: "csrftoken_demo",
    } as Window["__ENV__"];
    document.cookie = "csrftoken=prod-token; path=/";
    document.cookie = "csrftoken_demo=demo-token; path=/";

    expect(getCsrfToken()).toBe("demo-token");
  });

  it("returns undefined without the cookie", () => {
    expect(getCsrfToken()).toBeUndefined();
  });
});
