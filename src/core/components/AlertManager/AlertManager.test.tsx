import { screen, render, waitFor } from "@testing-library/react";
import { AlertType } from "core/helpers/alert";
import { waitForDialog } from "core/helpers/testutils";
import { useListener } from "core/hooks/useEmitter";
import AlertManager from "./AlertManager";
import userEvent from "@testing-library/user-event";

const useListenerMock = useListener as jest.Mock;

jest.mock("core/hooks/useEmitter", () => ({
  __esModule: true,
  useListener: jest.fn(),
}));

describe("AlertManager", () => {
  it("renders nothing by default", async () => {
    const { container } = render(<AlertManager />);
    expect(container).toMatchInlineSnapshot(`<div />`);
  });

  it("mounts an Alert dialog when an alert has to be shown", async () => {
    const user = userEvent.setup();
    const { container } = render(<AlertManager />);
    expect(useListenerMock.mock.calls[0][0]).toBe("displayAlert");

    // Trigger the callback with a fake alert event
    const cb = useListenerMock.mock.calls[0][1];
    expect(useListenerMock.mock.calls.length).toBe(1);
    await waitFor(async () => {
      cb({ detail: { message: "MESSAGE", type: AlertType.error } });
    });

    await waitForDialog();
    expect(screen.getByText("MESSAGE")).toBeInTheDocument();
    const btn = screen.getByRole("button", { name: "Close" });
    expect(btn).toBeInTheDocument();

    await user.click(btn);

    const dialog = await screen.queryByRole("dialog");
    expect(dialog).toBe(null);
  });
});
