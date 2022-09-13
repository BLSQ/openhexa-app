import Checkbox from "./Checkbox";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

const CHECKBOX_ID = "checkbox";

describe("Checkbox", () => {
  it("renders", async () => {
    render(<Checkbox data-testid={CHECKBOX_ID} />);

    const elm: HTMLInputElement = screen.getByTestId(CHECKBOX_ID);
    expect(elm).toBeInTheDocument();

    expect(elm.checked).toEqual(false);
    await userEvent.click(elm);
    expect(elm.checked).toEqual(true);
  });

  it("calls onChange on click", async () => {
    const onChange = jest.fn();
    render(<Checkbox data-testid={CHECKBOX_ID} checked onChange={onChange} />);

    const elm: HTMLInputElement = screen.getByTestId(CHECKBOX_ID);
    expect(elm.checked).toEqual(true);

    expect(onChange).not.toHaveBeenCalled();
    await userEvent.click(elm);
    expect(onChange).toHaveBeenCalled();
  });

  it("does not call onChange if disabled and clicked", async () => {
    const onChange = jest.fn();
    render(<Checkbox disabled={true} onChange={onChange} />);

    const elm: HTMLInputElement = screen.getByRole("checkbox");
    expect(onChange).not.toHaveBeenCalled();
    expect(elm).not.toBeChecked();
    await userEvent.click(elm);
    expect(elm).not.toBeChecked();
  });

  it("displays a label and a description if provided", () => {
    render(<Checkbox description="Description" label={"Label"} />);

    expect(screen.getByText("Description")).toBeInTheDocument();
    expect(screen.getByText("Label")).toBeInTheDocument();
  });
});
