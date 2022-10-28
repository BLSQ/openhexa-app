import Combobox from "./Combobox";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useEffect, useState } from "react";

const ComboboxWrapper = (props: React.ComponentProps<typeof Combobox>) => {
  const [value, setValue] = useState<any>(props.value);

  const onChange = (value: any) => {
    setValue(value);
    props.onChange(value);
  };

  useEffect(() => setValue(props.value), [props.value]);
  return <Combobox {...props} value={value} onChange={onChange} />;
};

const options = [
  {
    id: "1",
    label: "Option 1",
  },
  {
    id: "2",
    label: "Option 2",
  },
  {
    id: "3",
    label: "Option 3",
  },
];

describe("Combobox", () => {
  it("renders", async () => {
    const onChange = jest.fn();
    const onInputChange = jest.fn();
    const displayValue = jest.fn().mockReturnValue("<display value>");

    const { container, debug } = render(
      <ComboboxWrapper
        onChange={onChange}
        value={undefined}
        onInputChange={onInputChange}
        displayValue={displayValue}
        data-testid="combobox"
      >
        {options.map((option) => (
          <Combobox.CheckOption key={option.id} value={option}>
            {option.label}
          </Combobox.CheckOption>
        ))}
      </ComboboxWrapper>
    );
    const comboboxButton = screen.getByTestId("combobox-button");
    const comboboxInput = screen.getByTestId("combobox-input");
    expect(comboboxButton).toBeInTheDocument();
    expect(comboboxInput).toBeInTheDocument();

    expect(onInputChange).not.toHaveBeenCalled();
    expect(onChange).not.toHaveBeenCalled();
    expect(await screen.queryByTestId("combobox-options")).toBe(null);

    await waitFor(async () => {
      await fireEvent.click(comboboxButton);
      expect(screen.getByTestId("combobox-options")).toBeInTheDocument();
      const allOptions = container.getElementsByTagName("li");
      expect(allOptions.length === 3).toBeTruthy();
      await userEvent.click(allOptions[1]);
    });

    expect(onChange).toHaveBeenCalledWith(options[1]);
  });

  it("displays a loader when loading", () => {
    const onChange = jest.fn();
    const onInputChange = jest.fn();
    const displayValue = jest.fn().mockReturnValue("<display value>");

    const { container, debug } = render(
      <ComboboxWrapper
        onChange={onChange}
        value={undefined}
        loading
        onInputChange={onInputChange}
        displayValue={displayValue}
        data-testid="combobox"
      >
        {options.map((option) => (
          <Combobox.CheckOption key={option.id} value={option}>
            {option.label}
          </Combobox.CheckOption>
        ))}
      </ComboboxWrapper>
    );
    expect(screen.getByTestId("spinner")).toBeInTheDocument();
  });

  it("renders an icon when provided", () => {
    const onChange = jest.fn();
    const onInputChange = jest.fn();
    const displayValue = jest.fn().mockReturnValue("<display value>");
    const renderIcon = jest.fn().mockReturnValue(null);

    const { container, debug } = render(
      <ComboboxWrapper
        onChange={onChange}
        value={options[0]}
        loading
        onInputChange={onInputChange}
        displayValue={displayValue}
        renderIcon={renderIcon}
        data-testid="combobox"
      >
        {options.map((option) => (
          <Combobox.CheckOption key={option.id} value={option}>
            {option.label}
          </Combobox.CheckOption>
        ))}
      </ComboboxWrapper>
    );
    expect(renderIcon).toHaveBeenCalledWith(options[0]);
    expect(displayValue).toHaveBeenCalledWith(options[0]);
  });
});
