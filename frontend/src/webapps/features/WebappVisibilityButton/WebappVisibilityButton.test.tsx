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

beforeEach(() => jest.clearAllMocks());

describe("WebappVisibilityButton", () => {
  it("is hidden for members who cannot update the web app", () => {
    renderButton(buildWebapp({ permissions: { update: false } }));
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("does not change visibility until the user confirms", async () => {
    const mock = updateMock(true);
    renderButton(buildWebapp(), [mock]);

    fireEvent.click(screen.getByRole("button", { name: "Make public" }));
    expect(
      await screen.findByText("Make this web app public?"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("https://my-app.webapps.openhexa.org/"),
    ).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    await waitFor(() =>
      expect(
        screen.queryByText("Make this web app public?"),
      ).not.toBeInTheDocument(),
    );
    expect(mock.result).not.toHaveBeenCalled();
  });

  it("makes a private web app public after confirmation", async () => {
    const mock = updateMock(true);
    renderButton(buildWebapp(), [mock]);

    fireEvent.click(screen.getByRole("button", { name: "Make public" }));
    const dialogButtons = await screen.findAllByRole("button", {
      name: "Make public",
    });
    fireEvent.click(dialogButtons[dialogButtons.length - 1]);

    await waitFor(() => expect(mock.result).toHaveBeenCalled());
    await waitFor(() =>
      expect(toast.success).toHaveBeenCalledWith("Web app is now public"),
    );
  });

  it("keeps the dialog content while the new visibility reaches the cache", async () => {
    const { rerender } = renderButton(buildWebapp());

    fireEvent.click(screen.getByRole("button", { name: "Make public" }));
    expect(
      await screen.findByText("Make this web app public?"),
    ).toBeInTheDocument();

    rerender(
      <TestApp mocks={[]}>
        <WebappVisibilityButton webapp={buildWebapp({ isPublic: true })} />
      </TestApp>,
    );

    expect(screen.getByText("Make this web app public?")).toBeInTheDocument();
    expect(
      screen.queryByText("Make this web app private?"),
    ).not.toBeInTheDocument();
  });

  it("makes a public web app private after confirmation", async () => {
    const mock = updateMock(false);
    renderButton(buildWebapp({ isPublic: true }), [mock]);

    fireEvent.click(screen.getByRole("button", { name: "Make private" }));
    const dialogButtons = await screen.findAllByRole("button", {
      name: "Make private",
    });
    fireEvent.click(dialogButtons[dialogButtons.length - 1]);

    await waitFor(() => expect(mock.result).toHaveBeenCalled());
    await waitFor(() =>
      expect(toast.success).toHaveBeenCalledWith("Web app is now private"),
    );
  });

  // Only static apps go through the API proxy, so the warning is irrelevant elsewhere.
  it("warns about losing API access only for static web apps", async () => {
    renderButton(buildWebapp({ type: WebappType.Iframe }));

    fireEvent.click(screen.getByRole("button", { name: "Make public" }));
    await screen.findByText("Make this web app public?");

    expect(
      screen.queryByText(/Public web apps can't call the OpenHEXA API/),
    ).not.toBeInTheDocument();
  });
});
