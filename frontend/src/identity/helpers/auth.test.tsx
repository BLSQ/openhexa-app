import router from "next/router";
import { logout } from "./auth";

async function mockFetch() {
  return {
    ok: true,
    status: 302,
    url: "/login",
  };
}

describe("logout", () => {
  beforeAll(() => jest.spyOn(window, "fetch"));
  beforeEach(() => (window.fetch = mockFetch as jest.Mock));
  it("redirects the user to the logout page", async () => {
    const spyReplace = jest.spyOn(router, "replace");
    Object.defineProperty(window.document, "cookie", {
      value: "csrftoken=1234",
    });

    await logout();
    expect(spyReplace).toHaveBeenCalledWith("/login");
  });
});
