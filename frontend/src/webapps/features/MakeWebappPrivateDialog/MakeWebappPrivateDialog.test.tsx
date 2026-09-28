import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { TestApp } from "core/helpers/testutils";
import MakeWebappPrivateDialog from "./MakeWebappPrivateDialog";

jest.mock("next-i18next", () => ({
  useTranslation: jest.fn().mockReturnValue({ t: (key: string) => key }),
  Trans: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

const renderDialog = (
  props: Partial<{ onConfirm: () => Promise<void>; onClose: () => void }> = {},
) =>
  render(
    <TestApp mocks={[]}>
      <MakeWebappPrivateDialog
        open
        onClose={props.onClose ?? jest.fn()}
        onConfirm={props.onConfirm ?? jest.fn().mockResolvedValue(undefined)}
        webapp={{ name: "My app" }}
      />
    </TestApp>,
  );

describe("MakeWebappPrivateDialog", () => {
  it("warns that users without an account lose access", () => {
    renderDialog();

    expect(
      screen.getByText(
        /will no longer be accessible to users without an OpenHEXA account/,
      ),
    ).toBeInTheDocument();
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
