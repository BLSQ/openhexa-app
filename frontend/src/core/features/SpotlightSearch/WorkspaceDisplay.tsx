import { gql } from "@apollo/client";
import React from "react";
import Flag from "react-world-flags";
import { WorkspaceDisplayFragmentFragment } from "./WorkspaceDisplay.generated";

type WorkspaceDisplayProps = {
  workspace: WorkspaceDisplayFragmentFragment;
};

const WorkspaceDisplay = ({ workspace }: WorkspaceDisplayProps) => {
  return (
    <div className="flex items-center gap-1">
      {workspace.countries?.[0]?.code && (
        <Flag code={workspace.countries[0].code} className="w-5 h-4" />
      )}
      <span>{workspace.name}</span>
    </div>
  );
};

WorkspaceDisplay.fragments = {
  workspace: gql`
    fragment WorkspaceDisplayFragment on Workspace {
      name
      countries {
        code
      }
    }
  `,
};
export default WorkspaceDisplay;
