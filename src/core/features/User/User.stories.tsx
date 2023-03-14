import { Story, action } from "@ladle/react";
import React from "react";
import User from "./User";

export const UserStory: Story<
  { textColor?: string; subtext?: boolean } & React.ComponentProps<
    typeof User
  >["user"]
> = ({ textColor, subtext, ...user }) => (
  <User user={user} textColor={textColor} subtext={subtext} />
);

UserStory.storyName = "default";
UserStory.args = {
  textColor: "text-teal-500",
  subtext: true,
  id: "1",
  email: "alfonsebrown@openhexa.org",
  displayName: "Alfonse Brown",
  avatar: {
    initials: "AB",
    color: "purple",
  },
};
UserStory.argTypes = {};

const defaults = { title: "core / User" };

export default defaults;
