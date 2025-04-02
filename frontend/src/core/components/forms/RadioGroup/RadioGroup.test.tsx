import RadioGroup from "./RadioGroup";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

const options = [
  { id: "1", label: "Option 1" },
  { id: "2", label: "Option 2" },
  { id: "3", label: "Option 3" },
];

describe("RadioGroup", () => {
  it("renders", async () => {
    const onChange = jest.fn();
    const { container, debug } = render(
      <RadioGroup
        name="radio"
        onChange={onChange}
        value={"2"}
        options={options}
      />,
    );

    const selectedOption: HTMLInputElement | null =
      container.querySelector('input[checked=""]');

    expect(selectedOption).not.toBeNull();
    expect(selectedOption!.getAttribute("value")).toEqual("2");
    expect(container).toMatchSnapshot();

    await userEvent.click(screen.getByLabelText("Option 1"));

    expect(onChange).toHaveBeenCalled();
    expect(onChange.mock.calls[0][0].target.value).toBe("1");
  });

  it("does not trigger onChange if disabled", async () => {
    const onChange = jest.fn();
    const { container, debug } = render(
      <RadioGroup
        name="radio"
        onChange={onChange}
        disabled
        value={"2"}
        options={options}
      />,
    );

    await userEvent.click(screen.getByLabelText("Option 1"));

    expect(onChange).not.toHaveBeenCalled();
  });
});
