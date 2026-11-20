import { getSafeRedirectPath } from "../redirect";

describe("getSafeRedirectPath", () => {
  it.each(["/", "/dashboard", "/oauth/authorize/?client_id=abc&scope=x"])(
    "keeps the same-origin path %s",
    (next) => {
      expect(getSafeRedirectPath(next)).toBe(next);
    },
  );

  it.each([
    "https://evil.com",
    "http://evil.com/path",
    "//evil.com",
    "/\\evil.com",
    "\\\\evil.com",
    "/\t/evil.com",
    "/\n/evil.com",
    "javascript:alert(1)",
    " javascript:alert(1)",
    "",
  ])("falls back to / for %s", (next) => {
    expect(getSafeRedirectPath(next)).toBe("/");
  });

  it.each([undefined, null, ["/a", "/b"]])("falls back to / for %p", (next) => {
    expect(getSafeRedirectPath(next)).toBe("/");
  });
});
