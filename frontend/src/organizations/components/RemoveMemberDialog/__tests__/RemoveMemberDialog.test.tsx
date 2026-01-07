import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useDeleteOrganizationMemberMutation } from "organizations/features/OrganizationMembers/OrganizationMembers.generated";
import { TestApp } from "core/helpers/testutils";
import RemoveMemberDialog from "../RemoveMemberDialog";
import { v4 } from "uuid";
import { OrganizationMembershipRole } from "graphql/types";

const MEMBER_ID = v4();

const MOCK_ORGANIZATION_MEMBER = {
  __typename: "OrganizationMembership" as const,
  id: MEMBER_ID,
  role: OrganizationMembershipRole.Member,
  user: {
    id: v4(),
    displayName: "John Doe",
  },
};

const MOCK_EXTERNAL_COLLABORATOR = {
  __typename: "ExternalCollaborator" as const,
  id: MEMBER_ID,
  user: {
    id: v4(),
    displayName: "Jane External",
  },
};

jest.mock(
  "organizations/features/OrganizationMembers/OrganizationMembers.generated",
  () => ({
    ...jest.requireActual(
      "organizations/features/OrganizationMembers/OrganizationMembers.generated",
    ),
    useDeleteOrganizationMemberMutation: jest.fn(),
  }),
);

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

describe("RemoveMemberDialog", () => {
  const mockOnClose = jest.fn();

  beforeEach(() => {
    useDeleteOrganizationMemberMutationMock.mockClear();
    mockOnClose.mockClear();
  });

  describe("Organization Member", () => {
    it("is displayed when open is true", async () => {
      useDeleteOrganizationMemberMutationMock.mockReturnValue([
        jest.fn(),
        { loading: false },
      ]);

      render(
        <TestApp mocks={[]}>
          <RemoveMemberDialog
            open={true}
            onClose={mockOnClose}
            member={MOCK_ORGANIZATION_MEMBER}
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
          <RemoveMemberDialog
            open={true}
            onClose={mockOnClose}
            member={MOCK_ORGANIZATION_MEMBER}
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
          <RemoveMemberDialog
            open={true}
            onClose={mockOnClose}
            member={MOCK_ORGANIZATION_MEMBER}
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
  });

  describe("External Collaborator", () => {
    it("displays external collaborator information correctly", async () => {
      useDeleteOrganizationMemberMutationMock.mockReturnValue([
        jest.fn(),
        { loading: false },
      ]);

      render(
        <TestApp mocks={[]}>
          <RemoveMemberDialog
            open={true}
            onClose={mockOnClose}
            member={MOCK_EXTERNAL_COLLABORATOR}
          />
        </TestApp>,
      );

      expect(screen.getByText("Jane External")).toBeInTheDocument();
    });

    it("successfully deletes an external collaborator", async () => {
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
          <RemoveMemberDialog
            open={true}
            onClose={mockOnClose}
            member={MOCK_EXTERNAL_COLLABORATOR}
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
    });
  });

  describe("Common functionality", () => {
    it("displays action buttons correctly", async () => {
      useDeleteOrganizationMemberMutationMock.mockReturnValue([
        jest.fn(),
        { loading: false },
      ]);

      render(
        <TestApp mocks={[]}>
          <RemoveMemberDialog
            open={true}
            onClose={mockOnClose}
            member={MOCK_ORGANIZATION_MEMBER}
          />
        </TestApp>,
      );

      expect(
        screen.getByRole("button", { name: "Cancel" }),
      ).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: "Remove" }),
      ).toBeInTheDocument();
    });

    it("closes dialog when cancel is clicked", async () => {
      useDeleteOrganizationMemberMutationMock.mockReturnValue([
        jest.fn(),
        { loading: false },
      ]);
      const user = userEvent.setup();

      render(
        <TestApp mocks={[]}>
          <RemoveMemberDialog
            open={true}
            onClose={mockOnClose}
            member={MOCK_ORGANIZATION_MEMBER}
          />
        </TestApp>,
      );

      const cancelButton = screen.getByRole("button", { name: "Cancel" });
      await user.click(cancelButton);

      expect(mockOnClose).toHaveBeenCalled();
    });

    it("shows loading state during deletion", async () => {
      let resolveMutation: (value: any) => void;
      const mutationPromise = new Promise((resolve) => {
        resolveMutation = resolve;
      });

      const mockDeleteMutation = jest.fn(() => mutationPromise);

      useDeleteOrganizationMemberMutationMock.mockReturnValue([
        mockDeleteMutation,
        { loading: false },
      ]);

      render(
        <TestApp mocks={[]}>
          <RemoveMemberDialog
            open={true}
            onClose={mockOnClose}
            member={MOCK_ORGANIZATION_MEMBER}
          />
        </TestApp>,
      );

      const removeButton = screen.getByRole("button", { name: "Remove" });
      fireEvent.click(removeButton);

      expect(
        await screen.findByRole("button", { name: "Removing..." }),
      ).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: "Removing..." }),
      ).toBeDisabled();

      resolveMutation!({
        data: {
          deleteOrganizationMember: {
            success: true,
            errors: [],
          },
        },
      });
    });
  });
});
