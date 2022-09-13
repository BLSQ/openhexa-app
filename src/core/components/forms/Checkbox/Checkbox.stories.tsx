import { Story, action } from "@ladle/react";

import Checkbox from "./Checkbox";

export const CheckboxStory: Story = (props) => (
  <Checkbox {...props} onChange={action("onChange")} />
);
CheckboxStory.storyName = "default";
CheckboxStory.args = {
  checked: false,
  name: "checkbox",
  label: "Checkbox label",
  description: "Description",
};
CheckboxStory.argTypes = {};

const defaults = {
  title: "UI / Forms / Checkbox",
};

export default defaults;
