import { render, screen } from "@testing-library/react";
import { OrganizationsQuery } from "organizations/graphql/queries.generated";
import OrganizationsPage from "pages/organizations";
import { TestApp } from "../../core/helpers/testutils";

const organizations = [
  { id: "1", name: "Organization 1" },
  { id: "2", name: "Organization 2" },
] as OrganizationsQuery["organizations"];

describe("OrganizationsPage", () => {
  it("renders a list of organizations", () => {
    render(
      <TestApp>
        <OrganizationsPage organizations={organizations} />
      </TestApp>,
    );

    expect(screen.getByText("Organization 1")).toBeInTheDocument();
    expect(screen.getByText("Organization 2")).toBeInTheDocument();
  });
});
