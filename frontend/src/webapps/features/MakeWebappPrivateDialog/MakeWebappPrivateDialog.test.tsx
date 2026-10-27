import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { TestApp } from "core/helpers/testutils";
import { WebappType } from "graphql/types";
import MakeWebappPrivateDialog from "./MakeWebappPrivateDialog";

jest.mock("next-i18next", () => ({
  useTranslation: jest.fn().mockReturnValue({ t: (key: string) => key }),
}));

const renderDialog = (
  props: Partial<{
    onConfirm: () => Promise<void>;
    onClose: () => void;
    type: WebappType;
  }> = {},
) =>
  render(
    <TestApp mocks={[]}>
      <MakeWebappPrivateDialog
        open
        onClose={props.onClose ?? jest.fn()}
        onConfirm={props.onConfirm ?? jest.fn().mockResolvedValue(undefined)}
        webapp={{ type: props.type ?? WebappType.Static }}
      />
    </TestApp>,
  );

describe("MakeWebappPrivateDialog", () => {
  it("warns that the public link stops working", () => {
    renderDialog();

    expect(
      screen.getByText(/The public link will stop working/),
    ).toBeInTheDocument();
  });

  it("explains how API requests run for a static web app", () => {
    renderDialog({ type: WebappType.Static });

    expect(
      screen.getByText(/run on behalf of the signed-in member/),
    ).toBeInTheDocument();
  });

  it("skips the API explanation for non-static web apps", () => {
    renderDialog({ type: WebappType.Iframe });

    expect(
      screen.queryByText(/run on behalf of the signed-in member/),
    ).not.toBeInTheDocument();
  });

  it("confirms only when the user clicks make private", () => {
    const onConfirm = jest.fn().mockResolvedValue(undefined);
    const onClose = jest.fn();
    renderDialog({ onConfirm, onClose });

    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    expect(onClose).toHaveBeenCalled();
    expect(onConfirm).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole("button", { name: "Make private" }));
    expect(onConfirm).toHaveBeenCalled();
  });

  it("disables the buttons while the confirmation is in progress", async () => {
    let resolve: () => void = () => {};
    const onConfirm = jest.fn(() => new Promise<void>((r) => (resolve = r)));
    renderDialog({ onConfirm });

    const confirmButton = screen.getByRole("button", { name: "Make private" });
    fireEvent.click(confirmButton);

    expect(confirmButton).toBeDisabled();
    expect(screen.getByRole("button", { name: "Cancel" })).toBeDisabled();

    resolve();
    await waitFor(() => expect(confirmButton).not.toBeDisabled());
  });
});
