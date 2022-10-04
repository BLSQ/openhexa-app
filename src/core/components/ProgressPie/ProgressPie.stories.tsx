import { Story } from "@ladle/react";

import ProgressPie, { ProgressPieProps } from "./ProgressPie";

interface ProgressPieStoryProps extends ProgressPieProps {}

export const ProgressPieStory: Story<ProgressPieStoryProps> = () => {
  return (
    <div className="flex gap-2">
      <ProgressPie progress={10} className="w-30 h-30" />
      <ProgressPie progress={30} className="w-30 h-30" />
    </div>
  );
};

ProgressPieStory.storyName = "ProgressPie";

const defaults = {
  title: "UI / ProgressPie",
};
export default defaults;
