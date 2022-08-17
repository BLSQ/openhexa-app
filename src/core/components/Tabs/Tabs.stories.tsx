import { Story } from "@ladle/react";

import Tabs, { TabsProps } from "./Tabs";

interface TabsStoryProps extends TabsProps {}

export const TabsStory: Story<TabsStoryProps> = ({ children }) => {
  return (
    <Tabs defaultIndex={1}>
      <Tabs.Tab label="First tab label">
        <span>First Tab</span>
      </Tabs.Tab>
      <Tabs.Tab label="Second tab label">
        <span>Second Tab</span>
      </Tabs.Tab>
    </Tabs>
  );
};

TabsStory.storyName = "Tabs";

const defaults = {
  title: "UI / Tabs",
};
export default defaults;
