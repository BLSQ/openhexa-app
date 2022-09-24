import { Story } from "@ladle/react";

import ProgressPie, { ProgressPieProps } from "./ProgressPie";

interface ProgressPieStoryProps extends ProgressPieProps {}

export const ProgressPieStory: Story<ProgressPieStoryProps> = () => {
  return (
    <div>
      <ProgressPie progress={10} />
      <ProgressPie progress={30} size={50} />
    </div>
  );
};

ProgressPieStory.storyName = "ProgressPie";

const defaults = {
  title: "UI / ProgressPie",
};
export default defaults;
