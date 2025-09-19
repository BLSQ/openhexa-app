import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useDeleteOrganizationMemberMutation } from "../OrganizationMembers.generated";
import { TestApp } from "core/helpers/testutils";
import DeleteOrganizationMemberDialog from "../DeleteOrganizationMemberDialog";
import { v4 } from "uuid";
import { OrganizationMembershipRole } from "graphql/types";

const MEMBER_ID = v4();

const MOCK_MEMBER = {
  id: MEMBER_ID,
  role: OrganizationMembershipRole.Member,
  user: {
    id: v4(),
    displayName: "John Doe",
  },
};

jest.mock("../OrganizationMembers.generated", () => ({
  ...jest.requireActual("../OrganizationMembers.generated"),
  useDeleteOrganizationMemberMutation: jest.fn(),
}));

jest.mock("next-i18next", () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
  Trans: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  i18n: {
    t: (key: string) => key,
  },
}));

const useDeleteOrganizationMemberMutationMock =
  useDeleteOrganizationMemberMutation as jest.Mock;

describe("DeleteOrganizationMemberDialog", () => {
  const mockOnClose = jest.fn();

  beforeEach(() => {
    useDeleteOrganizationMemberMutationMock.mockClear();
    mockOnClose.mockClear();
  });

  it("is displayed when open is true", async () => {
    useDeleteOrganizationMemberMutationMock.mockReturnValue([
      jest.fn(),
      { loading: false },
    ]);

    render(
      <TestApp mocks={[]}>
        <DeleteOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          member={MOCK_MEMBER}
        />
      </TestApp>,
    );

    const dialog = screen.getByRole("dialog");
    expect(dialog).toBeInTheDocument();
    expect(screen.getByText("Remove Member")).toBeInTheDocument();
  });

  it("displays member information correctly", async () => {
    useDeleteOrganizationMemberMutationMock.mockReturnValue([
      jest.fn(),
      { loading: false },
    ]);

    render(
      <TestApp mocks={[]}>
        <DeleteOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          member={MOCK_MEMBER}
        />
      </TestApp>,
    );

    expect(
      screen.getByText(/Are you sure you want to remove/),
    ).toBeInTheDocument();
    expect(screen.getByText("John Doe")).toBeInTheDocument();
    expect(
      screen.getByText(/from this organization and associated workspaces/),
    ).toBeInTheDocument();
  });

  it("displays action buttons correctly", async () => {
    useDeleteOrganizationMemberMutationMock.mockReturnValue([
      jest.fn(),
      { loading: false },
    ]);

    render(
      <TestApp mocks={[]}>
        <DeleteOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          member={MOCK_MEMBER}
        />
      </TestApp>,
    );

    expect(screen.getByRole("button", { name: "Cancel" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Remove" })).toBeInTheDocument();
  });

  it("closes dialog when cancel is clicked", async () => {
    useDeleteOrganizationMemberMutationMock.mockReturnValue([
      jest.fn(),
      { loading: false },
    ]);
    const user = userEvent.setup();

    render(
      <TestApp mocks={[]}>
        <DeleteOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          member={MOCK_MEMBER}
        />
      </TestApp>,
    );

    const cancelButton = screen.getByRole("button", { name: "Cancel" });
    await user.click(cancelButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it("successfully deletes a member", async () => {
    const mockDeleteMutation = jest.fn().mockResolvedValue({
      data: {
        deleteOrganizationMember: {
          success: true,
          errors: [],
        },
      },
    });

    useDeleteOrganizationMemberMutationMock.mockReturnValue([
      mockDeleteMutation,
      { loading: false },
    ]);

    const user = userEvent.setup();

    render(
      <TestApp mocks={[]}>
        <DeleteOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          member={MOCK_MEMBER}
        />
      </TestApp>,
    );

    const removeButton = screen.getByRole("button", { name: "Remove" });
    await user.click(removeButton);

    await waitFor(() => {
      expect(mockDeleteMutation).toHaveBeenCalledWith({
        variables: {
          input: {
            id: MEMBER_ID,
          },
        },
      });
    });
    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  it("shows loading state during deletion", async () => {
    const mockDeleteMutation = jest.fn(() =>
      Promise.resolve({
        data: {
          deleteOrganizationMember: {
            success: true,
            errors: [],
          },
        },
      }),
    );

    useDeleteOrganizationMemberMutationMock.mockReturnValue([
      mockDeleteMutation,
      { loading: false },
    ]);

    render(
      <TestApp mocks={[]}>
        <DeleteOrganizationMemberDialog
          open={true}
          onClose={mockOnClose}
          member={MOCK_MEMBER}
        />
      </TestApp>,
    );

    const removeButton = screen.getByRole("button", { name: "Remove" });
    fireEvent.click(removeButton);

    expect(
      await screen.findByRole("button", { name: "Removing..." }),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Removing..." })).toBeDisabled();
  });
});
