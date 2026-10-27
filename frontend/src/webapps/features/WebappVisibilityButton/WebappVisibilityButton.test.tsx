import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MockedResponse } from "@apollo/client/testing";
import { toast } from "react-toastify";
import { TestApp } from "core/helpers/testutils";
import { WebappType } from "graphql/types";
import { UpdateWebappDocument } from "webapps/graphql/mutations.generated";
import WebappVisibilityButton from "./WebappVisibilityButton";

jest.mock("react-toastify", () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

jest.mock("next-i18next", () => ({
  useTranslation: jest.fn().mockReturnValue({ t: (key: string) => key }),
}));

const buildWebapp = (isPublic: boolean, update = true) => ({
  __typename: "Webapp" as const,
  id: "1",
  type: WebappType.Static,
  isPublic,
  serveUrl: "https://my-app.example/",
  permissions: { __typename: "WebappPermissions" as const, update },
});

const updateMock = (isPublic: boolean): MockedResponse => ({
  request: {
    query: UpdateWebappDocument,
    variables: { input: { id: "1", isPublic } },
  },
  result: {
    data: { updateWebapp: { success: true, errors: [], webapp: null } },
  },
});

describe("WebappVisibilityButton", () => {
  it("renders nothing without the update permission", () => {
    render(
      <TestApp mocks={[]}>
        <WebappVisibilityButton webapp={buildWebapp(false, false)} />
      </TestApp>,
    );

    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("asks for confirmation before making a private web app public", async () => {
    const mock = updateMock(true);
    render(
      <TestApp mocks={[mock]}>
        <WebappVisibilityButton webapp={buildWebapp(false)} />
      </TestApp>,
    );

    fireEvent.click(screen.getByRole("button", { name: "Make public" }));
    expect(screen.getByText("Make this web app public?")).toBeInTheDocument();

    fireEvent.click(
      screen.getAllByRole("button", { name: "Make public" }).at(-1)!,
    );

    await waitFor(() =>
      expect(
        screen.queryByText("Make this web app public?"),
      ).not.toBeInTheDocument(),
    );
    expect(toast.error).not.toHaveBeenCalled();
  });

  it("asks for confirmation before making a public web app private", async () => {
    render(
      <TestApp mocks={[updateMock(false)]}>
        <WebappVisibilityButton webapp={buildWebapp(true)} />
      </TestApp>,
    );

    fireEvent.click(screen.getByRole("button", { name: "Make private" }));
    expect(screen.getByText("Make this web app private?")).toBeInTheDocument();

    fireEvent.click(
      screen.getAllByRole("button", { name: "Make private" }).at(-1)!,
    );

    await waitFor(() =>
      expect(
        screen.queryByText("Make this web app private?"),
      ).not.toBeInTheDocument(),
    );
  });

  it("keeps the dialog open and shows an error when the update fails", async () => {
    const mock: MockedResponse = {
      request: {
        query: UpdateWebappDocument,
        variables: { input: { id: "1", isPublic: true } },
      },
      result: {
        data: {
          updateWebapp: {
            success: false,
            errors: ["PERMISSION_DENIED"],
            webapp: null,
          },
        },
      },
    };
    render(
      <TestApp mocks={[mock]}>
        <WebappVisibilityButton webapp={buildWebapp(false)} />
      </TestApp>,
    );

    fireEvent.click(screen.getByRole("button", { name: "Make public" }));
    fireEvent.click(
      screen.getAllByRole("button", { name: "Make public" }).at(-1)!,
    );

    await waitFor(() => expect(toast.error).toHaveBeenCalled());
    expect(screen.getByText("Make this web app public?")).toBeInTheDocument();
  });
});
