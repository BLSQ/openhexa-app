import { Story, action } from "@ladle/react";
import React, { useState } from "react";
import Combobox from "./Combobox";

export const ComboboxStory: Story<
  React.ComponentProps<typeof Combobox> & { options: any[] }
> = ({ options, ...delegated }) => {
  const [value, setValue] = useState<any | null>(options[0]);

  const onChange = (value: any) => {
    setValue(value);
  };
  return (
    <Combobox<any>
      {...delegated}
      onChange={onChange}
      value={value}
      displayValue={(v) => v.label}
    >
      {options.map((option) => (
        <Combobox.CheckOption key={option.label} value={option}>
          {option.label}
        </Combobox.CheckOption>
      ))}
    </Combobox>
  );
};

ComboboxStory.storyName = "default";
ComboboxStory.args = {
  placeholder: "Select something",
  options: [{ label: "Option 1" }, { label: "Option 2" }],
};
ComboboxStory.argTypes = {};

const defaults = { title: "UI / Forms / Combobox" };

export default defaults;
