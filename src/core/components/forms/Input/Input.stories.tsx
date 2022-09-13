import { Story } from "@ladle/react";
import Input from "./Input";

export const InputStory: Story = (props) => <Input {...props} />;

InputStory.storyName = "default";
InputStory.args = {};
InputStory.argTypes = {};

const defaults = { title: "UI / Forms / Input" };

export default defaults;
