import { MockedResponse } from "@apollo/client/testing";
import { act, renderHook, waitFor } from "@testing-library/react";
import { TestApp } from "core/helpers/testutils";
import { ReactNode } from "react";
import { toast } from "react-toastify";
import { GenerateWorkspaceTokenDocument } from "workspaces/graphql/mutations.generated";
import useWorkspaceAccessToken from "./useWorkspaceAccessToken";

jest.mock("react-toastify", () => ({ toast: { error: jest.fn() } }));

const TOKEN = "signed-access-token";

const buildMock = (success = true): MockedResponse => ({
  request: {
    query: GenerateWorkspaceTokenDocument,
    variables: { input: { slug: "my-workspace" } },
  },
  result: {
    data: {
      generateWorkspaceToken: {
        __typename: "GenerateWorkspaceTokenResult",
        success,
        errors: success ? [] : ["PERMISSION_DENIED"],
        token: success ? TOKEN : null,
      },
    },
  },
});

const renderUseWorkspaceAccessToken = (mocks: MockedResponse[]) =>
  renderHook(() => useWorkspaceAccessToken("my-workspace"), {
    wrapper: ({ children }: { children: ReactNode }) => (
      <TestApp mocks={mocks}>{children}</TestApp>
    ),
  });

describe("useWorkspaceAccessToken", () => {
  it("fetches nothing until the token is asked for", () => {
    const { result } = renderUseWorkspaceAccessToken([buildMock()]);

    expect(result.current.revealedToken).toBeNull();
  });

  it("keeps the token when hidden, so revealing it again costs no request", async () => {
    // A single mock: a second request would fail the test, which is the point.
    const { result } = renderUseWorkspaceAccessToken([buildMock()]);

    await act(() => result.current.toggle());
    await waitFor(() => expect(result.current.revealedToken).toEqual(TOKEN));

    await act(() => result.current.toggle());
    expect(result.current.revealedToken).toBeNull();

    await act(() => result.current.toggle());
    expect(result.current.revealedToken).toEqual(TOKEN);
  });

  it("reports a refused token instead of revealing nothing", async () => {
    const { result } = renderUseWorkspaceAccessToken([buildMock(false)]);

    await act(() => result.current.toggle());

    await waitFor(() =>
      expect(toast.error).toHaveBeenCalledWith(
        "Failed to retrieve the access token",
      ),
    );
    expect(result.current.revealedToken).toBeNull();
  });
});
