import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { act, useState } from "react";
import Drawer from "./Drawer";

import { assertVisible } from "core/helpers/testutils";

describe("Drawer", () => {
  it("renders", async () => {
    await render(
      <Drawer open={true} setOpen={() => {}}>
        <Drawer.Title>Title</Drawer.Title>
      </Drawer>,
    );

    await waitFor(() => {
      expect(screen.getByText("Title")).toBeInTheDocument();
      expect(screen.getByRole("dialog")).toBeInTheDocument();
    });
  });

  it("is visible when open is true", async () => {
    render(
      <Drawer open={true} setOpen={() => {}}>
        <Drawer.Title>Title</Drawer.Title>
      </Drawer>,
    );

    await waitFor(() => {
      const dialog = screen.getByRole("dialog");
      expect(dialog).toHaveAttribute("data-headlessui-state", "open");
      expect(dialog).toHaveAttribute("data-open");
    });
  });

  it("is hidden when open is false", async () => {
    await act(() =>
      render(
        <Drawer open={false} setOpen={() => {}}>
          <Drawer.Title>Title</Drawer.Title>
        </Drawer>,
      ),
    );
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("opens when trigger is clicked", async () => {
    function Test() {
      const [open, setOpen] = useState(false);
      return (
        <>
          <button id="trigger" onClick={() => setOpen(!open)}>
            Trigger
          </button>
          <Drawer open={open} setOpen={setOpen}>
            <Drawer.Title>Title</Drawer.Title>
          </Drawer>
        </>
      );
    }
    await render(<Test />);
    expect(screen.queryByRole("dialog")).toBeNull();
    const trigger = screen.getByRole("button", { name: "Trigger" });
    await userEvent.click(trigger);
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    assertVisible(screen.getByRole("dialog"));
  });

  it("closes when backdrop is clicked", async () => {
    const user = userEvent.setup();
    function Test() {
      const [open, setOpen] = useState(true);
      return (
        <>
          <button id="trigger" onClick={() => setOpen(!open)}>
            Trigger
          </button>
          <Drawer open={open} setOpen={setOpen} autoFocus={false}>
            <Drawer.Title>Title</Drawer.Title>
          </Drawer>
        </>
      );
    }
    await render(<Test />);

    assertVisible(screen.queryByRole("dialog"));

    await user.keyboard("{Escape}");
    await waitFor(() => {
      expect(screen.queryByRole("dialog")).toBeNull();
    });
  });
});
