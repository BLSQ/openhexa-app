import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { TestApp } from "core/helpers/testutils";
import { toast } from "react-toastify";
import RestoreWebappVersionDialog from "./RestoreWebappVersionDialog";
import { RestoreWebappVersionDocument } from "webapps/graphql/mutations.generated";

jest.mock("next-i18next", () => ({
  useTranslation: jest.fn().mockReturnValue({ t: (key: string) => key }),
  Trans: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));
jest.mock("react-toastify", () => ({
  toast: { success: jest.fn(), error: jest.fn() },
}));

const VERSION = "ccccccc3333333333333333333333333333333333";

const restoreMock = (success: boolean) => ({
  request: {
    query: RestoreWebappVersionDocument,
    variables: { input: { id: "webapp-1", versionId: VERSION } },
  },
  result: {
    data: {
      restoreWebappVersion: {
        __typename: "RestoreWebappVersionResult",
        success,
        errors: success ? [] : ["RESTORE_FAILED"],
        webapp: success
          ? {
              __typename: "Webapp",
              id: "webapp-1",
              source: {
                __typename: "GitSource",
                publishedVersion: "d".repeat(40),
              },
            }
          : null,
      },
    },
  },
});

describe("RestoreWebappVersionDialog", () => {
  beforeEach(() => jest.clearAllMocks());

  it("asks for confirmation and restores on confirm", async () => {
    const onClose = jest.fn();
    const onRestored = jest.fn();
    render(
      <TestApp mocks={[restoreMock(true)]}>
        <RestoreWebappVersionDialog
          open
          onClose={onClose}
          webappId="webapp-1"
          versionId={VERSION}
          onRestored={onRestored}
        />
      </TestApp>,
    );

    expect(screen.getByText("ccccccc")).toBeInTheDocument();
    expect(onRestored).not.toHaveBeenCalled();

    fireEvent.click(screen.getByTestId("confirm-restore"));

    await waitFor(() => expect(onRestored).toHaveBeenCalledTimes(1));
    expect(onClose).toHaveBeenCalled();
    expect(toast.success).toHaveBeenCalledWith(
      "Version restored and published",
    );
  });

  it("cancels without restoring", () => {
    const onClose = jest.fn();
    const onRestored = jest.fn();
    render(
      <TestApp mocks={[]}>
        <RestoreWebappVersionDialog
          open
          onClose={onClose}
          webappId="webapp-1"
          versionId={VERSION}
          onRestored={onRestored}
        />
      </TestApp>,
    );

    fireEvent.click(screen.getByText("Cancel"));
    expect(onClose).toHaveBeenCalled();
    expect(onRestored).not.toHaveBeenCalled();
  });

  it("keeps the dialog open and reports a failed restore", async () => {
    const onClose = jest.fn();
    const onRestored = jest.fn();
    render(
      <TestApp mocks={[restoreMock(false)]}>
        <RestoreWebappVersionDialog
          open
          onClose={onClose}
          webappId="webapp-1"
          versionId={VERSION}
          onRestored={onRestored}
        />
      </TestApp>,
    );

    fireEvent.click(screen.getByTestId("confirm-restore"));

    await waitFor(() =>
      expect(toast.error).toHaveBeenCalledWith("Failed to restore version"),
    );
    expect(onRestored).not.toHaveBeenCalled();
    expect(onClose).not.toHaveBeenCalled();
  });
});
