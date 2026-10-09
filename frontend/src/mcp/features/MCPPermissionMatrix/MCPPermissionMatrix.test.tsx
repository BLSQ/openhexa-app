import { render, screen } from "@testing-library/react";
import { McpResource, WorkspaceMembershipRole } from "graphql/types";

import MCPPermissionMatrix, { MCPGrant } from "./MCPPermissionMatrix";

const VIEWER_NOTE =
  "You are a viewer in {{count}} of the selected workspaces: there, the assistant can only do what a viewer can, whatever you choose below.";

const tools = [
  {
    name: "list_pipelines",
    description: "",
    resource: McpResource.Pipelines,
    write: false,
  },
  {
    name: "run_pipeline",
    description: "",
    resource: McpResource.Pipelines,
    write: true,
  },
];

const workspaces = [
  {
    slug: "viewed",
    name: "Viewed",
    countries: [],
    currentMembership: { role: WorkspaceMembershipRole.Viewer },
  },
  {
    slug: "edited",
    name: "Edited",
    countries: [],
    currentMembership: { role: WorkspaceMembershipRole.Editor },
  },
];

const renderMatrix = (grant: MCPGrant) =>
  render(
    <MCPPermissionMatrix
      idPrefix="test"
      grant={grant}
      workspaces={workspaces}
      tools={tools}
      onChange={jest.fn()}
    />,
  );

describe("MCPPermissionMatrix", () => {
  it("warns that a viewer workspace limits write tools", () => {
    renderMatrix({
      workspaceSlugs: ["viewed", "edited"],
      tools: ["list_pipelines", "run_pipeline"],
    });

    expect(screen.getByText(VIEWER_NOTE)).toBeInTheDocument();
  });

  it("tags the workspaces the person only views", () => {
    renderMatrix({ workspaceSlugs: [], tools: [] });

    expect(screen.getAllByText("Viewer")).toHaveLength(1);
    expect(screen.getByText("Viewed").closest("label")).toHaveTextContent(
      "Viewer",
    );
  });

  it("does not warn when no selected workspace is viewed only", () => {
    renderMatrix({
      workspaceSlugs: ["edited"],
      tools: ["list_pipelines", "run_pipeline"],
    });

    expect(screen.queryByText(VIEWER_NOTE)).not.toBeInTheDocument();
  });

  it("does not warn when the grant is read only", () => {
    renderMatrix({
      workspaceSlugs: ["viewed", "edited"],
      tools: ["list_pipelines"],
    });

    expect(screen.queryByText(VIEWER_NOTE)).not.toBeInTheDocument();
  });
});
