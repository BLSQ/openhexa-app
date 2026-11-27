import router from "next/router";
import { resetMixpanel } from "core/helpers/mixpanel";
import { logout } from "./auth";

jest.mock("core/helpers/mixpanel", () => ({
  resetMixpanel: jest.fn(),
}));

const resetMixpanelMock = resetMixpanel as jest.Mock;

async function mockFetch() {
  return {
    ok: true,
    status: 302,
    url: "/login",
  };
}

function setDocumentCookie(cookie: string) {
  Object.defineProperty(window.document, "cookie", {
    configurable: true,
    value: cookie,
  });
}

describe("logout", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    window.fetch = mockFetch as jest.Mock;
    setDocumentCookie("csrftoken=1234");
  });

  it("resets Mixpanel before redirecting the user to the logout page", async () => {
    const spyReplace = jest.spyOn(router, "replace");

    await logout();

    expect(resetMixpanelMock).toHaveBeenCalledTimes(1);
    expect(spyReplace).toHaveBeenCalledWith("/login");
    expect(resetMixpanelMock.mock.invocationCallOrder[0]).toBeLessThan(
      spyReplace.mock.invocationCallOrder[0],
    );
  });

  it("does not reset Mixpanel when the logout request fails", async () => {
    const spyReplace = jest.spyOn(router, "replace");
    window.fetch = jest.fn().mockRejectedValue(new Error("Network error"));

    await expect(logout()).rejects.toThrow("Network error");
    expect(resetMixpanelMock).not.toHaveBeenCalled();
    expect(spyReplace).not.toHaveBeenCalled();
  });

  it("does not reset Mixpanel when the CSRF token is missing", async () => {
    setDocumentCookie("");

    await expect(logout()).rejects.toThrow(
      "Could not find CSRF token in cookies.",
    );
    expect(resetMixpanelMock).not.toHaveBeenCalled();
  });
});
