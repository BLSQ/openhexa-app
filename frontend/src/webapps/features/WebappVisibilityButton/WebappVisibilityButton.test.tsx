import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MockedResponse } from "@apollo/client/testing";
import { TestApp } from "core/helpers/testutils";
import { WebappType } from "graphql/types";
import { toast } from "react-toastify";
import { UpdateWebappDocument } from "webapps/graphql/mutations.generated";
import WebappVisibilityButton from "./WebappVisibilityButton";

jest.mock("react-toastify", () => ({
  toast: { success: jest.fn(), error: jest.fn() },
}));

jest.mock("next-i18next", () => ({
  useTranslation: jest.fn().mockReturnValue({ t: (key: string) => key }),
}));

const buildWebapp = (overrides: any = {}) => ({
  __typename: "Webapp" as const,
  id: "webapp-1",
  type: WebappType.Static,
  isPublic: false,
  url: null,
  serveUrl: "https://my-app.webapps.openhexa.org/",
  permissions: { update: true },
  ...overrides,
});

const updateMock = (isPublic: boolean): MockedResponse => ({
  request: {
    query: UpdateWebappDocument,
    variables: { input: { id: "webapp-1", isPublic } },
  },
  result: jest.fn(() => ({
    data: {
      updateWebapp: {
        __typename: "UpdateWebappResult",
        success: true,
        errors: [],
        webapp: {
          __typename: "Webapp",
          id: "webapp-1",
          isPublic,
          allowedOperations: [],
          url: null,
          source: { __typename: "GitSource", publishedVersion: null },
        },
      },
    },
  })),
});

const renderButton = (webapp: any, mocks: MockedResponse[] = []) =>
  render(
    <TestApp mocks={mocks}>
      <WebappVisibilityButton webapp={webapp} />
    </TestApp>,
  );

const openAndChoose = async (label: string) => {
  fireEvent.click(screen.getByRole("button", { name: "Share" }));
  fireEvent.click(
    await screen.findByRole("radio", { name: new RegExp(`^${label}`) }),
  );
};

const PUBLIC_WARNING =
  "Anyone with the link will be able to open this web app without an OpenHEXA account. You can make it private again at any time.";

beforeEach(() => jest.clearAllMocks());

describe("WebappVisibilityButton", () => {
  it("is hidden for members who cannot update the web app", () => {
    renderButton(buildWebapp({ permissions: { update: false } }));
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("does not change visibility until the user saves", async () => {
    const mock = updateMock(true);
    renderButton(buildWebapp(), [mock]);

    await openAndChoose("Public");
    expect(screen.getByText(PUBLIC_WARNING)).toBeInTheDocument();
    expect(
      screen.getByText("https://my-app.webapps.openhexa.org/"),
    ).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    await waitFor(() =>
      expect(screen.queryByText(PUBLIC_WARNING)).not.toBeInTheDocument(),
    );
    expect(mock.result).not.toHaveBeenCalled();
  });

  it("makes a private web app public", async () => {
    const mock = updateMock(true);
    renderButton(buildWebapp(), [mock]);

    await openAndChoose("Public");
    fireEvent.click(screen.getByRole("button", { name: "Save" }));

    await waitFor(() => expect(mock.result).toHaveBeenCalled());
    await waitFor(() =>
      expect(toast.success).toHaveBeenCalledWith("Web app is now public"),
    );
  });

  it("keeps the dialog content while the new visibility reaches the cache", async () => {
    const { rerender } = renderButton(buildWebapp());

    await openAndChoose("Public");
    expect(screen.getByText(PUBLIC_WARNING)).toBeInTheDocument();

    rerender(
      <TestApp mocks={[]}>
        <WebappVisibilityButton webapp={buildWebapp({ isPublic: true })} />
      </TestApp>,
    );

    expect(screen.getByText(PUBLIC_WARNING)).toBeInTheDocument();
  });

  it("makes a public web app private", async () => {
    const mock = updateMock(false);
    renderButton(buildWebapp({ isPublic: true }), [mock]);

    await openAndChoose("Private");
    expect(
      screen.getByText(/The public link will stop working/),
    ).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Save" }));

    await waitFor(() => expect(mock.result).toHaveBeenCalled());
    await waitFor(() =>
      expect(toast.success).toHaveBeenCalledWith("Web app is now private"),
    );
  });

  // Only static apps go through the API proxy, so the warning is irrelevant elsewhere.
  it("warns about API access only for static web apps", async () => {
    renderButton(buildWebapp({ type: WebappType.Iframe }));

    await openAndChoose("Public");

    expect(
      screen.queryByText(/only reach the workspace's public resources/),
    ).not.toBeInTheDocument();
  });
});
