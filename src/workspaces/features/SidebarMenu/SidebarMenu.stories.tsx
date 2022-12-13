import { Story, action } from "@ladle/react";
import React from "react";
import { WORKSPACES } from "workspaces/helpers/fixtures";
import SidebarMenu from "./SidebarMenu";

export const SidebarMenuStory: Story<
  React.ComponentProps<typeof SidebarMenu>
> = (props) => <SidebarMenu {...props} workspace={WORKSPACES[0]} />;

SidebarMenuStory.storyName = "default";
SidebarMenuStory.args = {};
SidebarMenuStory.argTypes = {};

const defaults = { title: "Workspaces / SidebarMenu" };

export default defaults;
