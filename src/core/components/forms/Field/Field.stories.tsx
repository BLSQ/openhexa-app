import { Story, action } from "@ladle/react";

import Field from "./Field";
import Input from "../Input";
import Checkbox from "../Checkbox";

export const FieldStory: Story<React.ComponentProps<typeof Field>> = (
  props,
) => (
  <div className="space-y-4">
    <Field {...props}>
      <Input value="" placeholder="This one is dynamic" onChange={() => {}} />
    </Field>

    <Field
      name="number"
      label={"number"}
      required
      help="Help text"
      type="number"
      value={42}
      onChange={() => {}}
    />
  </div>
);
FieldStory.storyName = "default";
FieldStory.args = {
  required: false,
  label: "Field label",
  description: "",
  name: "",
  className: "",
  labelColor: "",
  errorColor: "",
  error: "",
};

FieldStory.argTypes = {};

const defaults = {
  title: "UI / Forms / Field",
};

export default defaults;
