import { getApolloClient } from "core/helpers/apollo";
import router from "next/router";
import { logout } from "./auth";

jest.mock("core/helpers/apollo");

const getApolloClientMock = getApolloClient as jest.Mock & {
  mutate: jest.Mock;
};

describe("logout", () => {
  it("redirects the user on success", async () => {
    const spyPush = jest.spyOn(router, "push");
    getApolloClientMock.mutate.mockReturnValue({
      data: { logout: { success: true } },
    });
    await logout("/outer-space");
    expect(getApolloClientMock.mutate).toHaveBeenCalled();
    expect(spyPush).toHaveBeenCalledWith("/outer-space");
  });
  it("does nothing on error", async () => {
    const spyPush = jest.spyOn(router, "push");
    getApolloClientMock.mutate.mockReturnValue({
      data: { logout: { success: false } },
    });
    await logout("/outer-space");
    expect(getApolloClientMock.mutate).toHaveBeenCalled();
    expect(spyPush).not.toHaveBeenCalled();
  });
});
