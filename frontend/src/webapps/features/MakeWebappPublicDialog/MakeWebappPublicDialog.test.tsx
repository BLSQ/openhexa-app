import { fireEvent, render, screen } from "@testing-library/react";
import { TestApp } from "core/helpers/testutils";
import { WebappOperationScope } from "graphql/types";
import MakeWebappPublicDialog from "./MakeWebappPublicDialog";

jest.mock("next-i18next", () => ({
  useTranslation: jest.fn().mockReturnValue({ t: (key: string) => key }),
  Trans: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

const renderDialog = (
  allowedOperations: WebappOperationScope[],
  props: Partial<{ onConfirm: () => void; onClose: () => void }> = {},
) =>
  render(
    <TestApp mocks={[]}>
      <MakeWebappPublicDialog
        open
        onClose={props.onClose ?? jest.fn()}
        onConfirm={props.onConfirm ?? jest.fn()}
        webapp={{ name: "My app", allowedOperations }}
      />
    </TestApp>,
  );

describe("MakeWebappPublicDialog", () => {
  it("warns that the web app becomes reachable without signing in", () => {
    renderDialog([]);

    expect(
      screen.getByText(/Anyone on the internet will be able to open/),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Visitors will not need an OpenHEXA account/),
    ).toBeInTheDocument();
  });

  it("lists only the operations that are switched on", () => {
    renderDialog([
      WebappOperationScope.DatasetsRead,
      WebappOperationScope.PipelinesRun,
    ]);

    expect(screen.getByText("Read datasets")).toBeInTheDocument();
    expect(screen.getByText("Run pipelines")).toBeInTheDocument();
    expect(screen.queryByText("Write datasets")).not.toBeInTheDocument();
    expect(screen.queryByText("Read files")).not.toBeInTheDocument();
  });

  it("says so when the web app has no API access", () => {
    renderDialog([]);

    expect(
      screen.getByText("This web app has no API access to your workspace."),
    ).toBeInTheDocument();
  });

  it("announces the AI security review", () => {
    renderDialog([]);

    expect(
      screen.getByText(/an AI security review will check this web app/),
    ).toBeInTheDocument();
  });

  it("confirms only when the review is started", () => {
    const onConfirm = jest.fn();
    const onClose = jest.fn();
    renderDialog([], { onConfirm, onClose });

    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    expect(onClose).toHaveBeenCalled();
    expect(onConfirm).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole("button", { name: "Start review" }));
    expect(onConfirm).toHaveBeenCalled();
  });
});
