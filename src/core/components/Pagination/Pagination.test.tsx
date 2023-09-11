import Pagination from "./Pagination";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

describe("Pagination", () => {
  const onChange = jest.fn();
  afterEach(() => {
    onChange.mockClear();
  });
  it("renders a pagination with two pages", async () => {
    const user = userEvent.setup();
    const { container, debug } = render(
      <Pagination
        page={1}
        perPage={15}
        onChange={onChange}
        totalItems={28}
        countItems={15}
        loading
      />,
    );
    const prevButton = screen.getByRole("button", { name: "Previous" });
    expect(prevButton).toBeInTheDocument();
    expect(prevButton).toBeDisabled();

    const nextButtons = screen.getAllByText("Next");
    expect(nextButtons.length).toBe(2);
    nextButtons.forEach((btn) => {
      expect(btn).not.toBeDisabled();
    });

    await user.click(prevButton);
    expect(onChange).not.toHaveBeenCalled();

    await user.click(nextButtons[1]);
    expect(onChange).toHaveBeenCalledWith(2, 15);
  });

  it("renders a loading state", async () => {
    const { container, debug } = render(
      <Pagination
        page={1}
        perPage={15}
        onChange={onChange}
        totalItems={28}
        countItems={15}
        loading
      />,
    );
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });
});
