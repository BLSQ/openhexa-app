import { Story, action } from "@ladle/react";
import React from "react";
import Block from "../Block";
import Button from "../Button";
import DescriptionList from "./DescriptionList";
import { DescriptionListDisplayMode } from "./helpers";

export const DescriptionListStory: Story<
  React.ComponentProps<typeof DescriptionList>
> = (props) => (
  <Block className="max-w-4xl p-4">
    <DescriptionList columns={props.columns} displayMode={props.displayMode}>
      <DescriptionList.Item label="First item">
        <span>And the first item value</span>
      </DescriptionList.Item>
      <DescriptionList.Item label="Second item">
        <p>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
          eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
          minim veniam, quis nostrud exercitation ullamco laboris nisi ut
          aliquip ex ea commodo consequat. Duis aute irure dolor in
          reprehenderit in voluptate velit esse cillum dolore.
        </p>
      </DescriptionList.Item>
      <DescriptionList.Item label="Third item">
        <Button>A button can be displayed</Button>
      </DescriptionList.Item>
    </DescriptionList>
  </Block>
);

DescriptionListStory.storyName = "default";
DescriptionListStory.args = {
  columns: 1,
};
DescriptionListStory.argTypes = {
  displayMode: {
    options: [
      DescriptionListDisplayMode.LABEL_ABOVE,
      DescriptionListDisplayMode.LABEL_LEFT,
    ],
    control: { type: "radio" },
    defaultValue: DescriptionListDisplayMode.LABEL_LEFT,
  },
};

const defaults = { title: "UI / DescriptionList" };

export default defaults;
