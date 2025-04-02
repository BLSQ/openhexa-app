import React, { useEffect, useState } from "react";
import { render, screen, waitFor } from "@testing-library/react";
import MultiCombobox from "./MultiCombobox";
import userEvent from "@testing-library/user-event";

type Item = { id: number; name: string };

const items: Item[] = [
  { id: 1, name: "Item 4" },
  { id: 2, name: "Item 2" },
  { id: 0, name: "Item 1" },
  { id: 3, name: "Item 3" },
];

const MultiComboboxWrapper = ({
  children,
  ...props
}: React.ComponentProps<typeof MultiCombobox>) => {
  const [value, setValue] = useState<any>(props.value);

  const onChange = (value: any) => {
    setValue([value]);
    props.onChange(value);
  };

  useEffect(() => setValue(props.value), [props.value]);
  return (
    <MultiCombobox {...props} value={value} onChange={onChange}>
      {children}
    </MultiCombobox>
  );
};

describe("MultiCombobox", () => {
  test("renders", async () => {
    const onChange = jest.fn();
    const onInputChange = jest.fn();
    render(
      <MultiComboboxWrapper
        value={[]}
        onChange={onChange}
        displayValue={(item: Item) => item.name}
        onInputChange={onInputChange}
        by={"name"}
      >
        {items.map((item) => (
          <MultiCombobox.CheckOption key={item.id} value={item}>
            {item.name}
          </MultiCombobox.CheckOption>
        ))}
      </MultiComboboxWrapper>,
    );

    const comboboxButton = screen.getByTestId("combobox-button");
    const comboboxInput = screen.getByTestId("combobox-input");
    expect(comboboxButton).toBeInTheDocument();
    expect(comboboxInput).toBeInTheDocument();

    expect(onInputChange).not.toHaveBeenCalled();
    expect(onChange).not.toHaveBeenCalled();

    await userEvent.click(comboboxButton);
    await waitFor(() => {
      expect(screen.getByTestId("combobox-options")).toBeInTheDocument();
    });

    const options = screen.getAllByRole("option");
    expect(options).toHaveLength(4);

    await userEvent.click(options[1]);
    await waitFor(() => {
      expect(onChange).toHaveBeenCalledWith([items[1]]);
    });

    expect(screen.getByText(items[1].name)).toBeInTheDocument();
  });
});
