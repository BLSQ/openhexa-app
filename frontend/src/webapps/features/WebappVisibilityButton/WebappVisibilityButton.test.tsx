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

const updateMock = (isPublic: boolean, success = true): MockedResponse => ({
  request: {
    query: UpdateWebappDocument,
    variables: { input: { id: "1", isPublic } },
  },
  result: {
    data: {
      updateWebapp: {
        success,
        errors: success ? [] : ["PERMISSION_DENIED"],
        webapp: null,
      },
    },
  },
});

describe("WebappVisibilityButton", () => {
  beforeEach(() => jest.clearAllMocks());

  it("renders nothing without the update permission", () => {
    render(
      <TestApp mocks={[]}>
        <WebappVisibilityButton webapp={buildWebapp(false, false)} />
      </TestApp>,
    );

    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("opens the share dialog and saves the new audience", async () => {
    render(
      <TestApp mocks={[updateMock(true)]}>
        <WebappVisibilityButton webapp={buildWebapp(false)} />
      </TestApp>,
    );

    fireEvent.click(screen.getByRole("button", { name: "Share" }));
    expect(screen.getByText("Share web app")).toBeInTheDocument();

    fireEvent.click(screen.getByLabelText(/Anyone with the link/));
    fireEvent.click(screen.getByTestId("share-save"));

    await waitFor(() =>
      expect(screen.queryByText("Share web app")).not.toBeInTheDocument(),
    );
    expect(toast.error).not.toHaveBeenCalled();
  });

  it("keeps the dialog open and shows an error when the update fails", async () => {
    render(
      <TestApp mocks={[updateMock(false, false)]}>
        <WebappVisibilityButton webapp={buildWebapp(true)} />
      </TestApp>,
    );

    fireEvent.click(screen.getByRole("button", { name: "Share" }));
    fireEvent.click(screen.getByLabelText(/Workspace members/));
    fireEvent.click(screen.getByTestId("share-save"));

    await waitFor(() => expect(toast.error).toHaveBeenCalled());
    expect(screen.getByText("Share web app")).toBeInTheDocument();
  });
});
