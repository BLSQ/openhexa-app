import { Cog6ToothIcon } from "@heroicons/react/24/outline";
import { Story } from "@ladle/react";
import React from "react";
import Button from "../Button";
import Card from "./Card";

export const CardStory: Story<React.ComponentProps<typeof Card>> = (props) => (
  <div className="m-6 flex gap-8">
    <Card title="Title of the card" subtitle="Hey">
      Content of the card which may longer than a usual sentence. That iss why I
      will add another sentence.
      <Card.Actions>
        <Button
          variant="secondary"
          leadingIcon={<Cog6ToothIcon className="w-4" />}
          size="sm"
        >
          An action
        </Button>
        <Button
          variant="white"
          leadingIcon={<Cog6ToothIcon className="w-4" />}
          size="sm"
        >
          Another action
        </Button>
        <Button leadingIcon={<Cog6ToothIcon className="w-4" />} size="sm">
          Test
        </Button>
      </Card.Actions>
    </Card>

    <Card>
      <Card.Header
        title="Lorem ipsum dolor sit amet"
        href="http://localhost:3000"
      />
      This is a card with a url
    </Card>
  </div>
);

CardStory.storyName = "default";
CardStory.args = {};
CardStory.argTypes = {};

const defaults = { title: "UI / Card" };

export default defaults;
