import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import OrganizationMembersPage from "pages/organizations/[organizationId]/members";
import { v4 } from "uuid";
import { ReactNode } from "react";

jest.mock("next-i18next", () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
  Trans: ({ children }: { children: ReactNode }) => <>{children}</>,
  i18n: {
    t: (key: string) => key,
  },
}));

const ORGANIZATION_ID = v4();

const MOCK_ORGANIZATION = {
  id: ORGANIZATION_ID,
  name: "Test Organization",
  shortName: "test-org",
  members: {
    totalItems: 5,
    items: [],
  },
  permissions: {
    manageMembers: true,
    createWorkspace: true,
    archiveWorkspace: true,
  },
  workspaces: {
    items: [
      {
        slug: "workspace-1",
        name: "Test Workspace 1",
        countries: [],
      },
    ],
  },
};

const MOCK_ORGANIZATION_NO_PERMISSIONS = {
  ...MOCK_ORGANIZATION,
  permissions: {
    manageMembers: false,
    createWorkspace: false,
    archiveWorkspace: false,
  },
};

describe("OrganizationMembersPage", () => {
  it("renders page with organization information", async () => {
    render(
      <TestApp>
        <OrganizationMembersPage organization={MOCK_ORGANIZATION} />
      </TestApp>,
    );

    expect(screen.queryAllByText("Members").length).toBeGreaterThanOrEqual(1);

    expect(screen.getByText("5 members")).toBeInTheDocument();
  });

  it("displays singular member text when count is 1", async () => {
    const organizationWithOneMember = {
      ...MOCK_ORGANIZATION,
      members: {
        totalItems: 1,
        items: [],
      },
    };

    render(
      <TestApp mocks={[]}>
        <OrganizationMembersPage organization={organizationWithOneMember} />
      </TestApp>,
    );

    expect(screen.getByText("1 member")).toBeInTheDocument();
  });

  it("renders invite member button when user has permissions", async () => {
    render(
      <TestApp mocks={[]}>
        <OrganizationMembersPage organization={MOCK_ORGANIZATION} />
      </TestApp>,
    );

    const inviteButton = screen.getByRole("button", { name: /Invite member/i });
    expect(inviteButton).toBeInTheDocument();
    expect(inviteButton).not.toBeDisabled();
  });

  it("disables invite member button when user lacks permissions", async () => {
    render(
      <TestApp mocks={[]}>
        <OrganizationMembersPage
          organization={MOCK_ORGANIZATION_NO_PERMISSIONS}
        />
      </TestApp>,
    );

    const inviteButton = screen.getByRole("button", { name: /Invite member/i });
    expect(inviteButton).toBeInTheDocument();
    expect(inviteButton).toBeDisabled();
  });

  it("opens add member dialog when invite button is clicked", async () => {
    const user = userEvent.setup();

    render(
      <TestApp mocks={[]}>
        <OrganizationMembersPage organization={MOCK_ORGANIZATION} />
      </TestApp>,
    );

    const inviteButton = screen.getByRole("button", { name: /Invite member/i });
    await user.click(inviteButton);

    expect(
      screen.queryAllByText("Invite Member").length,
    ).toBeGreaterThanOrEqual(2);
  });

  it("closes add member dialog when onClose is called", async () => {
    const user = userEvent.setup();

    render(
      <TestApp mocks={[]}>
        <OrganizationMembersPage organization={MOCK_ORGANIZATION} />
      </TestApp>,
    );

    const inviteButton = screen.getByRole("button", { name: /Invite member/i });
    await user.click(inviteButton);

    const closeButton = screen.getByText("Cancel");
    await user.click(closeButton);

    await waitFor(() => {
      expect(screen.queryAllByText("Invite Member").length).toBeLessThanOrEqual(
        1,
      );
    });
  });

  it("displays pending invitations section", async () => {
    render(
      <TestApp mocks={[]}>
        <OrganizationMembersPage organization={MOCK_ORGANIZATION} />
      </TestApp>,
    );

    expect(screen.getByText("Pending invitations")).toBeInTheDocument();
  });

  it("handles organization without members data gracefully", async () => {
    const organizationWithoutMembers = {
      id: ORGANIZATION_ID,
      name: "Test Organization",
      shortName: "test-org",
      permissions: {
        manageMembers: true,
        createWorkspace: true,
        archiveWorkspace: true,
      },
      workspaces: {
        items: [],
      },
      members: {
        totalItems: 0,
        items: [],
      },
    };

    render(
      <TestApp mocks={[]}>
        <OrganizationMembersPage organization={organizationWithoutMembers} />
      </TestApp>,
    );

    expect(screen.getByText("0 member")).toBeInTheDocument();
  });
});
