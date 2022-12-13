import { Story } from "@ladle/react";
import BadgeProperty from "./BadgeProperty";

import DataCard, { DataCardProps } from "./DataCard";
import TextProperty from "./TextProperty";

interface DataCardStoryProps extends DataCardProps {}

export const DataCardStory: Story<DataCardStoryProps> = ({ children }) => {
  return (
    <DataCard
      item={{
        name: "Alfonse",
        description: `### Description Field

Hey It's in *italic*!`,
        tags: [{ label: "Hey" }, { label: "Tag" }],
      }}
    >
      <DataCard.Heading titleAccessor="name" />
      <DataCard.FormSection title="First Section">
        <TextProperty id="name" label="Name" accessor="name" />
        <TextProperty
          id="description"
          label="Description"
          accessor="description"
          markdown
        />
        <BadgeProperty id="tags" label="Badges" accessor="tags" />
      </DataCard.FormSection>
    </DataCard>
  );
};

DataCardStory.storyName = "DataCard";

const defaults = {
  title: "UI / DataCard",
};
export default defaults;
