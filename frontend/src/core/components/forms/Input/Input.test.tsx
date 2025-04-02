import { EyeIcon } from "@heroicons/react/24/outline";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Input from "../Input";

describe("Input", () => {
  it("renders", async () => {
    const onChange = jest.fn();
    const { container } = render(
      <Input data-testid="input" name="a_field" onChange={onChange} />,
    );
    expect(container).toMatchSnapshot();

    const input = screen.getByTestId("input");

    expect(input).not.toBeDisabled();
    expect(input).toHaveValue("");

    await userEvent.type(input, "This is the value");
    expect(onChange).toHaveBeenCalled();
  });

  it("renders a disabled input", async () => {
    const onChange = jest.fn();
    const { container } = render(
      <Input
        disabled
        name="a_field"
        value="Value"
        onChange={onChange}
        data-testid="input"
      />,
    );

    const input = screen.getByTestId("input");
    expect(input).toBeInTheDocument();
    expect(input).toBeDisabled();
    await userEvent.type(input, "New value");

    expect(input).toHaveValue("Value");
  });

  it("renders a trailing icon", () => {
    const { container } = render(
      <Input
        value={""}
        onChange={() => {}}
        trailingIcon={<EyeIcon className="w-4" />}
      />,
    );

    expect(container).toMatchSnapshot();
  });

  it("has an invalid status", () => {
    render(
      <Input error="Err" data-testid="input" value={""} onChange={() => {}} />,
    );

    const input = screen.getByTestId("input");

    expect(input.getAttribute("aria-invalid")).toBe("true");
    expect(input).toHaveClass("border-red-300");
  });
});
