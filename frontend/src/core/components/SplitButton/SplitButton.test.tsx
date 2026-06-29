import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import SplitButton from "./SplitButton";

// Headless UI's MenuButton toggles on pointer events, which jsdom does not
// implement; polyfill the minimum surface so the dropdown can open.
beforeAll(() => {
  (window as unknown as { PointerEvent: typeof MouseEvent }).PointerEvent =
    MouseEvent as unknown as typeof MouseEvent;
  Element.prototype.hasPointerCapture = jest.fn();
  Element.prototype.releasePointerCapture = jest.fn();
  Element.prototype.scrollIntoView = jest.fn();
});

const openMenu = async (menuLabel = "More options") => {
  await userEvent.click(screen.getByLabelText(menuLabel));
};

describe("SplitButton", () => {
  it("renders the primary label and fires the primary action", async () => {
    const onClick = jest.fn();
    render(<SplitButton label="Run" onClick={onClick} actions={[]} />);

    await userEvent.click(screen.getByRole("button", { name: "Run" }));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("shows the loading label while loading", () => {
    render(
      <SplitButton
        label="Run"
        loadingLabel="Running…"
        loading
        onClick={jest.fn()}
        actions={[]}
      />,
    );
    expect(screen.getByText("Running…")).toBeInTheDocument();
    expect(screen.queryByText("Run")).not.toBeInTheDocument();
  });

  it("disables the primary button when disabled", () => {
    render(
      <SplitButton label="Run" disabled onClick={jest.fn()} actions={[]} />,
    );
    expect(screen.getByRole("button", { name: "Run" })).toBeDisabled();
  });

  it("opens the menu and fires a secondary action", async () => {
    const onSelection = jest.fn();
    render(
      <SplitButton
        label="Run"
        onClick={jest.fn()}
        menuLabel="More run options"
        actions={[{ label: "Run selection", onClick: onSelection }]}
      />,
    );

    await openMenu("More run options");
    await userEvent.click(await screen.findByText("Run selection"));
    expect(onSelection).toHaveBeenCalledTimes(1);
  });

  it("does not fire a disabled action", async () => {
    const onClick = jest.fn();
    render(
      <SplitButton
        label="Run"
        onClick={jest.fn()}
        actions={[{ label: "Run all", onClick, disabled: true }]}
      />,
    );

    await openMenu();
    await userEvent.click(await screen.findByText("Run all"));
    expect(onClick).not.toHaveBeenCalled();
  });
});
