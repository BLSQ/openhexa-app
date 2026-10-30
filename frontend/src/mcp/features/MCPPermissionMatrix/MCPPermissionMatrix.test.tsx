import { fireEvent, render, screen } from "@testing-library/react";
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

const ministry = { id: "org-1", name: "Ministry" };
const partner = { id: "org-2", name: "Partner" };

const workspaces = [
  {
    slug: "viewed",
    name: "Viewed",
    countries: [],
    currentMembership: { role: WorkspaceMembershipRole.Viewer },
    organization: { id: ministry.id },
  },
  {
    slug: "edited",
    name: "Edited",
    countries: [],
    currentMembership: { role: WorkspaceMembershipRole.Editor },
    organization: { id: ministry.id },
  },
  {
    slug: "partnered",
    name: "Partnered",
    countries: [],
    currentMembership: { role: WorkspaceMembershipRole.Editor },
    organization: { id: partner.id },
  },
];

const renderMatrix = (
  grant: Omit<MCPGrant, "organizationIds"> & { organizationIds?: string[] },
  onChange = jest.fn(),
) =>
  render(
    <MCPPermissionMatrix
      idPrefix="test"
      grant={{ organizationIds: [], ...grant }}
      organizations={[ministry, partner]}
      workspaces={workspaces}
      tools={tools}
      onChange={onChange}
    />,
  );

const expandAll = () => {
  for (const toggle of screen.queryAllByRole("button", { expanded: false })) {
    fireEvent.click(toggle);
  }
};

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
    expandAll();

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

  it("selecting an organization replaces its individually picked workspaces", () => {
    const onChange = jest.fn();
    renderMatrix(
      { workspaceSlugs: ["edited", "partnered"], tools: [] },
      onChange,
    );

    fireEvent.click(screen.getByLabelText(/Ministry/));

    expect(onChange).toHaveBeenCalledWith({
      workspaceSlugs: ["partnered"],
      organizationIds: ["org-1"],
      tools: [],
    });
  });

  it("shows the workspaces of a granted organization as selected and locked", () => {
    renderMatrix({ workspaceSlugs: [], organizationIds: ["org-1"], tools: [] });
    expandAll();

    for (const slug of ["viewed", "edited"]) {
      const checkbox = document.getElementById(`test-workspace-${slug}`);
      expect(checkbox).toBeChecked();
      expect(checkbox).toBeDisabled();
    }
    expect(
      document.getElementById("test-workspace-partnered"),
    ).not.toBeChecked();
  });

  it("collapses each organization when there are several", () => {
    renderMatrix({ workspaceSlugs: [], tools: [] });

    expect(screen.queryByText("Viewed")).not.toBeInTheDocument();

    fireEvent.click(screen.getAllByRole("button", { expanded: false })[0]);

    expect(screen.getByText("Viewed")).toBeInTheDocument();
    expect(screen.queryByText("Partnered")).not.toBeInTheDocument();
  });

  it("starts open when there is a single organization", () => {
    render(
      <MCPPermissionMatrix
        idPrefix="test"
        grant={{ workspaceSlugs: [], organizationIds: [], tools: [] }}
        organizations={[ministry]}
        workspaces={workspaces.filter((w) => w.organization.id === ministry.id)}
        tools={tools}
        onChange={jest.fn()}
      />,
    );

    expect(screen.getByText("Viewed")).toBeInTheDocument();
  });

  it("lists an organization that has no workspace yet", () => {
    render(
      <MCPPermissionMatrix
        idPrefix="test"
        grant={{ workspaceSlugs: [], organizationIds: [], tools: [] }}
        organizations={[{ id: "org-3", name: "Newcomer" }]}
        workspaces={[]}
        tools={tools}
        onChange={jest.fn()}
      />,
    );

    expect(screen.getByLabelText(/Newcomer/)).toBeInTheDocument();
    expect(screen.getByText("No workspace yet")).toBeInTheDocument();
  });

  it("select all grants every organization", () => {
    const onChange = jest.fn();
    renderMatrix({ workspaceSlugs: ["edited"], tools: [] }, onChange);

    fireEvent.click(screen.getByText("Select all"));

    expect(onChange).toHaveBeenCalledWith({
      workspaceSlugs: [],
      organizationIds: ["org-1", "org-2"],
      tools: [],
    });
  });

  it("counts viewer workspaces reached through an organization", () => {
    renderMatrix({
      workspaceSlugs: [],
      organizationIds: ["org-1"],
      tools: ["list_pipelines", "run_pipeline"],
    });

    expect(screen.getByText(VIEWER_NOTE)).toBeInTheDocument();
  });
});
