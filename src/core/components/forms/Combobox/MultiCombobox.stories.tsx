import { Story } from "@ladle/react";
import React, { useState } from "react";
import MultiCombobox from "./MultiCombobox";

export const MultiComboboxStory: Story<
  React.ComponentProps<typeof MultiCombobox> & { options: any[] }
> = ({ options, ...delegated }) => {
  const [value, setValue] = useState<any[]>([options[0]]);

  const onChange = (value: any) => {
    setValue(value);
  };

  return (
    <MultiCombobox
      {...delegated}
      onChange={onChange}
      value={value}
      displayValue={(val) => val.label}
    >
      {options.map((option) => (
        <MultiCombobox.CheckOption key={option.label} value={option}>
          {option.label}
        </MultiCombobox.CheckOption>
      ))}
    </MultiCombobox>
  );
};

MultiComboboxStory.storyName = "default";
MultiComboboxStory.args = {
  placeholder: "Select something",
  options: [{ label: "Option 1" }, { label: "Option 2" }],
};
MultiComboboxStory.argTypes = {};

const defaults = { title: "UI / Forms / MultiCombobox" };

export default defaults;
