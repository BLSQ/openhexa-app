import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import Dialog from "./Dialog";
import { useState } from "react";
import userEvent from "@testing-library/user-event";
import { mockAnimationsApi } from "jsdom-testing-mocks";
mockAnimationsApi();

describe("Dialog", () => {
  it("renders", async () => {
    render(
      <Dialog open={true} onClose={() => {}}>
        <div>Test</div>
      </Dialog>,
    );
    await waitFor(() => {
      expect(screen.getByText("Test")).toBeInTheDocument();
    });
  });

  it("closes when clicking outside", async () => {
    const user = userEvent.setup();
    const Test = () => {
      const [open, setOpen] = useState(true);
      return (
        <>
          <button data-testid="btn">Button</button>
          <Dialog open={open} onClose={() => setOpen(false)}>
            <div>Test</div>
          </Dialog>
        </>
      );
    };
    render(<Test />);
    await waitFor(() => {
      expect(screen.getByText("Test")).toBeInTheDocument();
    });
    await user.click(screen.getByTestId("btn"));
    await waitFor(() => {
      expect(screen.queryByText("Test")).not.toBeInTheDocument();
    });
  });

  it("does not closes when clicking outside if persistent is true", async () => {
    const user = userEvent.setup();
    const Test = () => {
      const [open, setOpen] = useState(true);
      return (
        <>
          <button data-testid="btn">Button</button>
          <Dialog open={open} onClose={() => setOpen(false)} persistent>
            <div>Test</div>
          </Dialog>
        </>
      );
    };
    render(<Test />);
    await waitFor(() => {
      expect(screen.getByText("Test")).toBeInTheDocument();
    });
    await user.click(screen.getByTestId("btn"));
    await waitFor(() => {
      expect(screen.getByText("Test")).toBeInTheDocument();
    });
  });

  it("closes when pressing escape", async () => {
    const user = userEvent.setup();
    const Test = () => {
      const [open, setOpen] = useState(true);
      return (
        <Dialog open={open} onClose={() => setOpen(false)}>
          <Dialog.Content>Content</Dialog.Content>
        </Dialog>
      );
    };
    render(<Test />);
    await waitFor(() => {
      expect(screen.getByText("Content")).toBeInTheDocument();
    });
    await user.keyboard("{Escape}");
    await waitFor(() => {
      expect(screen.queryByText("Content")).not.toBeInTheDocument();
    });
  });

  it("does not close when pressing escape if closeOnEscape is false", async () => {
    const user = userEvent.setup();
    const Test = () => {
      const [open, setOpen] = useState(true);
      return (
        <Dialog open={open} onClose={() => setOpen(false)} closeOnEsc={false}>
          <Dialog.Content>Content</Dialog.Content>
        </Dialog>
      );
    };
    render(<Test />);
    await waitFor(() => {
      expect(screen.getByText("Content")).toBeInTheDocument();
    });
    await user.keyboard("{Escape}");
    await waitFor(() => {
      expect(screen.getByText("Content")).toBeInTheDocument();
    });
  });
});
