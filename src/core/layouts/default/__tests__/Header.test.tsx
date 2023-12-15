import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp, waitForDialog } from "core/helpers/testutils";
import mockRouter from "next-router-mock";
import Header from "../Header";

let hotkeyCb: Function;
jest.mock("react-hotkeys-hook", () => ({
  __esModule: true,
  useHotkeys: (keys: any, cb: any) => {
    hotkeyCb = cb;
  },
}));

describe("Header", () => {
  beforeEach(() => {
    mockRouter.setCurrentUrl("/");
  });

  it.skip("opens the search when clicked", async () => {
    const user = userEvent.setup();
    const { container } = render(
      <TestApp>
        <Header />
      </TestApp>,
    );

    const search = screen.getByText("Search");
    expect(search).toBeInTheDocument();

    await user.click(search);

    const dialog = await waitForDialog();
    expect(dialog).toBeInTheDocument();

    await user.click(container);
    await waitFor(() => {
      expect(dialog).not.toBeInTheDocument();
    });
  });

  it.skip("opens the search on control + k", async () => {
    render(
      <TestApp>
        <Header />
      </TestApp>,
    );

    const search = screen.getByText("Search");
    expect(search).toBeInTheDocument();
    waitFor(() => {
      hotkeyCb();
    });
    await waitFor(async () => {
      const dialog = await waitForDialog();
      expect(dialog).toBeInTheDocument();
    });
  });
});
