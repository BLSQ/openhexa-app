import { getApolloClient } from "core/helpers/apollo";
import router from "next/router";
import { logout } from "./auth";

jest.mock("core/helpers/apollo");

describe("logout", () => {
  it("redirects the user to the logout page", async () => {
    const spyPush = jest.spyOn(router, "push");
    await logout();
    expect(spyPush).toHaveBeenCalledWith("/auth/logout");
  });
});
