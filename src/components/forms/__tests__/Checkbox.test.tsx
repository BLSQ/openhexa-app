import Checkbox from "components/forms/Checkbox";
import { render, screen, fireEvent } from "@testing-library/react";

const CHECKBOX_ID = "checkbox";

describe("Checkbox", () => {
  it("renders", () => {
    render(<Checkbox data-testid={CHECKBOX_ID} />);

    const elm: HTMLInputElement = screen.getByTestId(CHECKBOX_ID);
    expect(elm).toBeInTheDocument();

    expect(elm.checked).toEqual(false);
    fireEvent.click(elm);
    expect(elm.checked).toEqual(true);
  });

  it("calls onChange on click", () => {
    const onChange = jest.fn();
    render(<Checkbox data-testid={CHECKBOX_ID} checked onChange={onChange} />);

    const elm: HTMLInputElement = screen.getByTestId(CHECKBOX_ID);
    expect(elm.checked).toEqual(true);

    expect(onChange).not.toHaveBeenCalled();
    fireEvent.click(elm);
    expect(onChange).toHaveBeenCalled();
  });
});
