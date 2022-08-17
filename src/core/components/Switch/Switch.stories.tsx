import { Story } from "@ladle/react";
import { useEffect, useState } from "react";

import Switch, { SwitchProps } from "./Switch";

interface StoryProps extends SwitchProps {}

export const SwitchStory: Story<StoryProps> = ({ checked, ...delegated }) => {
  const [isToggled, setToggled] = useState(checked);

  useEffect(() => {
    setToggled(checked);
  }, [checked]);

  return <Switch {...delegated} onChange={setToggled} checked={isToggled} />;
};

SwitchStory.storyName = "Switch";

const defaults = {
  title: "UI / Switch",
};

SwitchStory.args = {
  name: "switch",
  label: "Switch Label",
  checked: false,
  disabled: false,
};

export default defaults;
