import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MockedProvider } from "@apollo/client/testing";
import OrganizationPage from "pages/organizations/[organizationId]";
import { OrganizationQuery } from "organizations/graphql/queries.generated";
import { act } from "react";

jest.mock("next-i18next", () => ({
  useTranslation: jest.fn().mockReturnValue({ t: (key: string) => key }),
}));

const organization = {
  id: "org-1",
  name: "Test Organization",
  permissions: {
    createWorkspace: true,
    archiveWorkspace: true,
  },
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
    render(
      <MockedProvider>
        <OrganizationPage organization={null} />
      </MockedProvider>,
    );

    expect(screen.queryByText("Test Organization")).not.toBeInTheDocument();
  });

  it("opens create workspace dialog when 'Create Workspace' button is clicked", () => {
    render(
      <MockedProvider>
        <OrganizationPage organization={organization} />
      </MockedProvider>,
    );

    const createButton = screen.getByText("Create Workspace");
    fireEvent.click(createButton);

    expect(screen.getByText("Create a workspace")).toBeInTheDocument();
  });

  it("opens archive workspace dialog when 'Archive' button is clicked", () => {
    render(
      <MockedProvider>
        <OrganizationPage organization={organization} />
      </MockedProvider>,
    );

    const archiveButton = screen.getAllByText("Archive")[0];
    act(() => {
      fireEvent.click(archiveButton);
    });

    waitFor(() =>
      expect(screen.getByText("Archive Workspace 1")).toBeInTheDocument(),
    );
  });
});
