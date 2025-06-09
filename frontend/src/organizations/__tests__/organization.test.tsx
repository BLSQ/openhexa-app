import { render, screen } from "@testing-library/react";
import { OrganizationQuery } from "organizations/graphql/queries.generated";
import OrganizationPage from "pages/organizations/[organizationId]";
import { MockedProvider } from "@apollo/client/testing";

const organization = {
  name: "Test Organization",
  workspaces: {
    items: [
      { slug: "workspace-1", name: "Workspace 1", countries: [{ code: "US" }] },
      { slug: "workspace-2", name: "Workspace 2", countries: [] },
    ],
  },
} as OrganizationQuery["organization"];

describe("OrganizationPage", () => {
  it("renders organization name and workspaces", () => {
    render(
      <MockedProvider>
        <OrganizationPage organization={organization} />
      </MockedProvider>,
    );

    expect(screen.getAllByText("Test Organization")).toHaveLength(2);
    expect(screen.getByText("2 workspaces")).toBeInTheDocument();
    expect(screen.getByText("Workspace 1")).toBeInTheDocument();
    expect(screen.getByText("Workspace 2")).toBeInTheDocument();
  });

  it("renders nothing if organization is null", () => {
    render(<OrganizationPage organization={null} />);

    expect(screen.queryByText("Test Organization")).not.toBeInTheDocument();
  });
});
