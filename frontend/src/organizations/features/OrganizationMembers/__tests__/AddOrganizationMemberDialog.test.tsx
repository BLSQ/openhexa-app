import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useInviteOrganizationMemberMutation } from "../OrganizationMembers.generated";
import { TestApp } from "core/helpers/testutils";
import AddOrganizationMemberDialog from "../AddOrganizationMemberDialog";
import { v4 } from "uuid";
import {
  OrganizationMembershipRole,
  WorkspaceMembershipRole,
  InviteOrganizationMemberError,
} from "graphql/types";
import { ReactNode } from "react";

const ORGANIZATION_ID = v4();

const MOCK_ORGANIZATION = {
  id: ORGANIZATION_ID,
  name: "Test Organization",
  shortName: "test-org",
  permissions: {
    manageMembers: true,
    createWorkspace: true,
    archiveWorkspace: true,
    manageOwners: true,
  },
  members: {
    totalItems: 0,
    items: [],
  },
  workspaces: {
    totalItems: 2,
    items: [
      {
        slug: "workspace-1",
        name: "Test Workspace 1",
        countries: [],
      },
      {
        slug: "workspace-2",
        name: "Test Workspace 2",
        countries: [],
      },
    ],
  },
};

const MOCK_USER = {
  id: v4(),
  email: "newuser@example.com",
  displayName: "New User",
  avatar: {
    initials: "NU",
    color: "blue",
  },
};

jest.mock("../OrganizationMembers.generated", () => ({
  ...jest.requireActual("../OrganizationMembers.generated"),
  useInviteOrganizationMemberMutation: jest.fn(),
}));

jest.mock("next-i18next", () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
  Trans: ({ children }: { children: ReactNode }) => <>{children}</>,
  i18n: {
    t: (key: string) => key,
  },
}));

const useInviteOrganizationMemberMutationMock =
  useInviteOrganizationMemberMutation as jest.Mock;

describe("AddOrganizationMemberDialog", () => {
  const mockOnClose = jest.fn();

  beforeEach(() => {
    useInviteOrganizationMemberMutationMock.mockClear();
    mockOnClose.mockClear();
  });

  it("is displayed when open is true", async () => {
    useInviteOrganizationMemberMutationMock.mockReturnValue([jest.fn(), {}]);

    render(
      <TestApp mocks={[]}>
        <AddOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          organization={MOCK_ORGANIZATION}
        />
      </TestApp>,
    );

    const dialog = screen.getByRole("dialog");
    expect(dialog).toBeInTheDocument();
    expect(screen.queryAllByText("Invite Member").length).toBeGreaterThan(1);
  });

  it("displays form fields correctly", async () => {
    useInviteOrganizationMemberMutationMock.mockReturnValue([jest.fn(), {}]);

    render(
      <TestApp mocks={[]}>
        <AddOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          organization={MOCK_ORGANIZATION}
        />
      </TestApp>,
    );

    expect(screen.getByText("User")).toBeInTheDocument();
    expect(screen.getByText("Organization Role")).toBeInTheDocument();
    expect(screen.getByText("Workspaces")).toBeInTheDocument();

    expect(screen.getByText("Test Workspace 1")).toBeInTheDocument();
    expect(screen.getByText("Test Workspace 2")).toBeInTheDocument();
  });

  it("handles user selection", async () => {
    useInviteOrganizationMemberMutationMock.mockReturnValue([jest.fn(), {}]);
    const user = userEvent.setup();

    render(
      <TestApp mocks={[]}>
        <AddOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          organization={MOCK_ORGANIZATION}
        />
      </TestApp>,
    );

    const emailInput = screen.getByPlaceholderText("Enter email address");
    await user.type(emailInput, "newuser@example.com");

    expect(emailInput).toHaveValue("newuser@example.com");
  });

  it("handles organization role change", async () => {
    useInviteOrganizationMemberMutationMock.mockReturnValue([jest.fn(), {}]);
    const user = userEvent.setup();

    render(
      <TestApp mocks={[]}>
        <AddOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          organization={MOCK_ORGANIZATION}
        />
      </TestApp>,
    );

    const roleSelect = screen.getByDisplayValue("Member");
    await user.selectOptions(roleSelect, "Admin");

    expect(roleSelect).toHaveValue(OrganizationMembershipRole.Admin);
  });

  it("handles workspace role selection", async () => {
    useInviteOrganizationMemberMutationMock.mockReturnValue([jest.fn(), {}]);
    const user = userEvent.setup();

    render(
      <TestApp mocks={[]}>
        <AddOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          organization={MOCK_ORGANIZATION}
        />
      </TestApp>,
    );

    const adminRadio = screen
      .getAllByRole("radio")
      .find((radio) => radio.getAttribute("name")?.includes("workspace-1"));

    expect(adminRadio).toBeInTheDocument();
    expect(adminRadio).not.toBeChecked();
    await user.click(adminRadio!);
    expect(adminRadio).toBeChecked();
  });

  it("filters workspaces based on search", async () => {
    useInviteOrganizationMemberMutationMock.mockReturnValue([jest.fn(), {}]);
    const user = userEvent.setup();

    render(
      <TestApp mocks={[]}>
        <AddOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          organization={MOCK_ORGANIZATION}
        />
      </TestApp>,
    );

    const searchInput = screen.getByPlaceholderText("Search workspaces...");
    await user.type(searchInput, "Workspace 1");

    expect(screen.getByText("Test Workspace 1")).toBeInTheDocument();
    expect(screen.queryByText("Test Workspace 2")).not.toBeInTheDocument();
  });

  it("shows validation error when user is not selected", async () => {
    const mockInviteMutation = jest.fn();
    useInviteOrganizationMemberMutationMock.mockReturnValue([
      mockInviteMutation,
      {},
    ]);
    const user = userEvent.setup();

    render(
      <TestApp mocks={[]}>
        <AddOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          organization={MOCK_ORGANIZATION}
        />
      </TestApp>,
    );

    const submitButton = screen.getByRole("button", { name: "Invite Member" });
    await user.click(submitButton);

    expect(screen.getByText("Email address is mandatory")).toBeInTheDocument();
    expect(mockInviteMutation).not.toHaveBeenCalled();
  });

  it("successfully invites a member", async () => {
    const mockInviteMutation = jest.fn().mockResolvedValue({
      data: {
        inviteOrganizationMember: {
          success: true,
          errors: [],
        },
      },
    });

    useInviteOrganizationMemberMutationMock.mockReturnValue([
      mockInviteMutation,
      {},
    ]);
    const user = userEvent.setup();

    render(
      <TestApp mocks={[]}>
        <AddOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          organization={MOCK_ORGANIZATION}
        />
      </TestApp>,
    );

    const emailInput = screen.getByPlaceholderText("Enter email address");
    await user.type(emailInput, MOCK_USER.email);

    await waitFor(() => {
      expect(screen.getByText("Test Workspace 1")).toBeInTheDocument();
      expect(screen.getByText("Test Workspace 2")).toBeInTheDocument();
    });

    const viewerRadio1 = screen
      .getAllByRole("radio")
      .find((radio) => radio.getAttribute("name")?.includes("workspace-1"));
    const viewerRadio2 = screen
      .getAllByRole("radio")
      .find((radio) => radio.getAttribute("name")?.includes("workspace-2"));

    await user.click(viewerRadio1!);
    await user.click(viewerRadio2!);

    const submitButton = screen.getByRole("button", { name: "Invite Member" });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockInviteMutation).toHaveBeenCalledWith({
        variables: {
          input: {
            userEmail: MOCK_USER.email,
            organizationId: ORGANIZATION_ID,
            organizationRole: OrganizationMembershipRole.Member,
            workspaceInvitations: [
              {
                workspaceSlug: "workspace-1",
                workspaceName: "Test Workspace 1",
                role: WorkspaceMembershipRole.Admin,
              },
              {
                workspaceSlug: "workspace-2",
                workspaceName: "Test Workspace 2",
                role: WorkspaceMembershipRole.Admin,
              },
            ],
          },
        },
      });
    });

    expect(mockOnClose).toHaveBeenCalled();
  });

  it("handles permission denied error", async () => {
    const mockInviteMutation = jest.fn().mockResolvedValue({
      data: {
        inviteOrganizationMember: {
          success: false,
          errors: [InviteOrganizationMemberError.PermissionDenied],
        },
      },
    });

    useInviteOrganizationMemberMutationMock.mockReturnValue([
      mockInviteMutation,
      {},
    ]);
    const user = userEvent.setup();

    render(
      <TestApp mocks={[]}>
        <AddOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          organization={MOCK_ORGANIZATION}
        />
      </TestApp>,
    );

    const emailInput = screen.getByPlaceholderText("Enter email address");
    await user.type(emailInput, MOCK_USER.email);

    const submitButton = screen.getByRole("button", { name: "Invite Member" });
    await user.click(submitButton);

    await waitFor(() => {
      expect(
        screen.getByText("You are not authorized to perform this action"),
      ).toBeInTheDocument();
    });

    expect(mockOnClose).not.toHaveBeenCalled();
  });

  it("closes dialog when cancel is clicked", async () => {
    useInviteOrganizationMemberMutationMock.mockReturnValue([jest.fn(), {}]);
    const user = userEvent.setup();

    render(
      <TestApp mocks={[]}>
        <AddOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          organization={MOCK_ORGANIZATION}
        />
      </TestApp>,
    );

    const cancelButton = screen.getByText("Cancel");
    await user.click(cancelButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it("updates workspace roles when organization role changes", async () => {
    useInviteOrganizationMemberMutationMock.mockReturnValue([jest.fn(), {}]);
    const user = userEvent.setup();

    const { rerender } = render(
      <TestApp mocks={[]}>
        <AddOrganizationMemberDialog
          open={false}
          onClose={mockOnClose}
          organization={MOCK_ORGANIZATION}
        />
      </TestApp>,
    );

    rerender(
      <TestApp mocks={[]}>
        <AddOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          organization={MOCK_ORGANIZATION}
        />
      </TestApp>,
    );

    const roleSelect = screen.getByRole("combobox", {
      name: "Organization Role",
    });
    await waitFor(() => {
      expect(roleSelect).toBeInTheDocument();
    });

    const editorRadios = screen.getAllByRole("radio");
    expect(editorRadios.length).toBe(8);
    expect((editorRadios[1] as HTMLInputElement).checked).toBe(true);
    expect((editorRadios[2] as HTMLInputElement).checked).toBe(false);
    expect((editorRadios[5] as HTMLInputElement).checked).toBe(true);
    expect((editorRadios[6] as HTMLInputElement).checked).toBe(false);
    await user.selectOptions(roleSelect, OrganizationMembershipRole.Admin);
    expect((editorRadios[0] as HTMLInputElement).checked).toBe(true);
    expect((editorRadios[1] as HTMLInputElement).checked).toBe(false);
    expect((editorRadios[2] as HTMLInputElement).checked).toBe(false);
    expect((editorRadios[4] as HTMLInputElement).checked).toBe(true);
    expect((editorRadios[5] as HTMLInputElement).checked).toBe(false);
    expect((editorRadios[6] as HTMLInputElement).checked).toBe(false);
  });

  it("handles empty workspace list", async () => {
    useInviteOrganizationMemberMutationMock.mockReturnValue([jest.fn(), {}]);

    const organizationWithNoWorkspaces = {
      ...MOCK_ORGANIZATION,
      workspaces: { totalItems: 0, items: [] },
    };

    render(
      <TestApp mocks={[]}>
        <AddOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          organization={organizationWithNoWorkspaces}
        />
      </TestApp>,
    );

    expect(screen.getByText("No workspace available")).toBeInTheDocument();
  });
});
