import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useUpdateOrganizationMemberMutation } from "../OrganizationMembers.generated";
import { TestApp } from "core/helpers/testutils";
import UpdateOrganizationMemberDialog from "../UpdateOrganizationMemberDialog";
import { v4 } from "uuid";
import {
  OrganizationMembershipRole,
  WorkspaceMembershipRole,
  UpdateOrganizationMemberError,
} from "graphql/types";
import { ReactNode } from "react";

const ORGANIZATION_ID = v4();
const MEMBER_ID = v4();

const MOCK_MEMBER = {
  id: MEMBER_ID,
  role: OrganizationMembershipRole.Member,
  workspaceMemberships: [
    {
      id: v4(),
      role: WorkspaceMembershipRole.Viewer,
      workspace: {
        slug: "workspace-1",
        name: "Test Workspace 1",
      },
    },
    {
      id: v4(),
      role: WorkspaceMembershipRole.Editor,
      workspace: {
        slug: "workspace-2",
        name: "Test Workspace 2",
      },
    },
  ],
  user: {
    id: v4(),
    displayName: "John Doe",
    email: "john.doe@example.com",
  },
};

const MOCK_ORGANIZATION = {
  id: ORGANIZATION_ID,
  name: "Test Organization",
  permissions: {
    manageMembers: true,
    manageOwners: true,
  },
  members: {
    totalItems: 0,
    items: [],
  },
  workspaces: {
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
      {
        slug: "workspace-3",
        name: "Test Workspace 3",
        countries: [],
      },
    ],
  },
};

jest.mock("../OrganizationMembers.generated", () => ({
  ...jest.requireActual("../OrganizationMembers.generated"),
  useUpdateOrganizationMemberMutation: jest.fn(),
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

const useUpdateOrganizationMemberMutationMock =
  useUpdateOrganizationMemberMutation as jest.Mock;

describe("UpdateOrganizationMemberDialog", () => {
  const mockOnClose = jest.fn();

  beforeEach(() => {
    useUpdateOrganizationMemberMutationMock.mockClear();
    mockOnClose.mockClear();
  });

  it("is displayed when open is true", async () => {
    useUpdateOrganizationMemberMutationMock.mockReturnValue([jest.fn(), {}]);

    render(
      <TestApp mocks={[]}>
        <UpdateOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          member={MOCK_MEMBER}
          organization={MOCK_ORGANIZATION}
        />
      </TestApp>,
    );

    const dialog = screen.getByRole("dialog");
    expect(dialog).toBeInTheDocument();
    expect(screen.getByText("Update Member Permissions")).toBeInTheDocument();
    expect(screen.getByText("Updating permissions for")).toBeInTheDocument();
    expect(screen.getByText("John Doe")).toBeInTheDocument();
  });

  it("displays member information and form fields correctly", async () => {
    useUpdateOrganizationMemberMutationMock.mockReturnValue([jest.fn(), {}]);

    render(
      <TestApp mocks={[]}>
        <UpdateOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          member={MOCK_MEMBER}
          organization={MOCK_ORGANIZATION}
        />
      </TestApp>,
    );

    expect(screen.getByText("John Doe")).toBeInTheDocument();

    expect(screen.getByText("Organization Role")).toBeInTheDocument();
    expect(screen.getByText("Workspaces")).toBeInTheDocument();

    expect(screen.getByDisplayValue("Member")).toBeInTheDocument();

    expect(screen.getByText("Test Workspace 1")).toBeInTheDocument();
    expect(screen.getByText("Test Workspace 2")).toBeInTheDocument();
    expect(screen.getByText("Test Workspace 3")).toBeInTheDocument();
  });

  it("pre-selects existing member roles correctly", async () => {
    useUpdateOrganizationMemberMutationMock.mockReturnValue([jest.fn(), {}]);

    render(
      <TestApp mocks={[]}>
        <UpdateOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          member={MOCK_MEMBER}
          organization={MOCK_ORGANIZATION}
        />
      </TestApp>,
    );

    const workspace1ViewerRadio = screen.getByRole("radio", {
      name: "workspace-1 VIEWER",
    });
    expect(workspace1ViewerRadio).toBeChecked();

    const workspace2EditorRadio = screen.getByRole("radio", {
      name: "workspace-2 EDITOR",
    });
    expect(workspace2EditorRadio).toBeChecked();

    const workspace3NoneRadio = screen.getByRole("radio", {
      name: "workspace-3 NONE",
    });
    expect(workspace3NoneRadio).toBeChecked();
  });

  it("handles organization role change", async () => {
    useUpdateOrganizationMemberMutationMock.mockReturnValue([jest.fn(), {}]);
    const user = userEvent.setup();

    render(
      <TestApp mocks={[]}>
        <UpdateOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          member={MOCK_MEMBER}
          organization={MOCK_ORGANIZATION}
        />
      </TestApp>,
    );

    const roleSelect = screen.getByDisplayValue("Member");
    await user.selectOptions(roleSelect, OrganizationMembershipRole.Admin);

    expect(roleSelect).toHaveValue(OrganizationMembershipRole.Admin);
  });

  it("handles workspace role changes", async () => {
    useUpdateOrganizationMemberMutationMock.mockReturnValue([jest.fn(), {}]);
    const user = userEvent.setup();

    render(
      <TestApp mocks={[]}>
        <UpdateOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          member={MOCK_MEMBER}
          organization={MOCK_ORGANIZATION}
        />
      </TestApp>,
    );

    const workspace1AdminRadio = screen.getByRole("radio", {
      name: "workspace-1 ADMIN",
    });

    expect(workspace1AdminRadio).not.toBeChecked();
    await user.click(workspace1AdminRadio);
    expect(workspace1AdminRadio).toBeChecked();
  });

  it("filters workspaces based on search", async () => {
    useUpdateOrganizationMemberMutationMock.mockReturnValue([jest.fn(), {}]);
    const user = userEvent.setup();

    render(
      <TestApp mocks={[]}>
        <UpdateOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          member={MOCK_MEMBER}
          organization={MOCK_ORGANIZATION}
        />
      </TestApp>,
    );

    const searchInput = screen.getByPlaceholderText("Search workspaces...");
    await user.type(searchInput, "Workspace 1");

    expect(screen.getByText("Test Workspace 1")).toBeInTheDocument();
    expect(screen.queryByText("Test Workspace 2")).not.toBeInTheDocument();
    expect(screen.queryByText("Test Workspace 3")).not.toBeInTheDocument();
  });

  it("successfully updates member permissions", async () => {
    const mockUpdateMutation = jest.fn().mockResolvedValue({
      data: {
        updateOrganizationMember: {
          success: true,
          errors: [],
          membership: {
            id: MEMBER_ID,
            role: OrganizationMembershipRole.Admin,
          },
        },
      },
    });

    useUpdateOrganizationMemberMutationMock.mockReturnValue([
      mockUpdateMutation,
      {},
    ]);
    const user = userEvent.setup();

    render(
      <TestApp mocks={[]}>
        <UpdateOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          member={MOCK_MEMBER}
          organization={MOCK_ORGANIZATION}
        />
      </TestApp>,
    );

    const roleSelect = screen.getByDisplayValue("Member");
    await user.selectOptions(roleSelect, OrganizationMembershipRole.Admin);

    const workspace1AdminRadio = screen.getByRole("radio", {
      name: "workspace-1 ADMIN",
    });
    await user.click(workspace1AdminRadio);

    const submitButton = screen.getByText("Update");
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockUpdateMutation).toHaveBeenCalledWith({
        variables: {
          input: {
            id: MEMBER_ID,
            role: OrganizationMembershipRole.Admin,
            workspacePermissions: [
              {
                workspaceSlug: "workspace-1",
                role: WorkspaceMembershipRole.Admin,
              },
              {
                workspaceSlug: "workspace-2",
                role: WorkspaceMembershipRole.Editor,
              },
              {
                workspaceSlug: "workspace-3",
                role: null,
              },
            ],
          },
        },
      });
    });

    expect(mockOnClose).toHaveBeenCalled();
  });

  it("handles permission denied error", async () => {
    const mockUpdateMutation = jest.fn().mockResolvedValue({
      data: {
        updateOrganizationMember: {
          success: false,
          errors: [UpdateOrganizationMemberError.PermissionDenied],
        },
      },
    });

    useUpdateOrganizationMemberMutationMock.mockReturnValue([
      mockUpdateMutation,
      {},
    ]);
    const user = userEvent.setup();

    render(
      <TestApp mocks={[]}>
        <UpdateOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          member={MOCK_MEMBER}
          organization={MOCK_ORGANIZATION}
        />
      </TestApp>,
    );

    const submitButton = screen.getByText("Update");
    await user.click(submitButton);

    await waitFor(() => {
      expect(
        screen.getByText("You are not authorized to perform this action"),
      ).toBeInTheDocument();
    });

    expect(mockOnClose).not.toHaveBeenCalled();
  });

  it("closes dialog when cancel is clicked", async () => {
    useUpdateOrganizationMemberMutationMock.mockReturnValue([jest.fn(), {}]);
    const user = userEvent.setup();

    render(
      <TestApp mocks={[]}>
        <UpdateOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          member={MOCK_MEMBER}
          organization={MOCK_ORGANIZATION}
        />
      </TestApp>,
    );

    const cancelButton = screen.getByText("Cancel");
    await user.click(cancelButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it("handles empty workspace search results", async () => {
    useUpdateOrganizationMemberMutationMock.mockReturnValue([jest.fn(), {}]);
    const user = userEvent.setup();

    render(
      <TestApp mocks={[]}>
        <UpdateOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          member={MOCK_MEMBER}
          organization={MOCK_ORGANIZATION}
        />
      </TestApp>,
    );

    const searchInput = screen.getByPlaceholderText("Search workspaces...");
    await user.type(searchInput, "nonexistent");

    expect(screen.getByText("No workspace found")).toBeInTheDocument();
  });
});
