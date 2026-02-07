import { Trans, useTranslation } from "next-i18next";
import Dialog from "core/components/Dialog";
import Button from "core/components/Button";
import { useDeleteOrganizationMemberMutation } from "organizations/features/OrganizationMembers/OrganizationMembers.generated";
import { useDeleteExternalCollaboratorMutation } from "organizations/features/OrganizationExternalCollaborators/OrganizationExternalCollaborators.generated";
import {
  DeleteOrganizationMemberError,
  DeleteExternalCollaboratorError,
} from "graphql/types";
import { useApolloClient, gql } from "@apollo/client";
import useForm from "core/hooks/useForm";
import { toast } from "react-toastify";
import { RemoveMemberDialog_MemberFragment } from "./RemoveMemberDialog.generated";

type RemoveMemberDialogProps = {
  open: boolean;
  onClose: () => void;
  member: RemoveMemberDialog_MemberFragment;
  organizationId?: string;
};

export default function RemoveMemberDialog({
  open,
  onClose,
  member,
  organizationId,
}: RemoveMemberDialogProps) {
  const { t } = useTranslation();
  const client = useApolloClient();

  const isOrganizationMember = member.__typename === "OrganizationMembership";

  const [deleteOrganizationMember] = useDeleteOrganizationMemberMutation({
    refetchQueries: [
      "OrganizationMembers",
      "OrganizationExternalCollaborators",
      "Organization",
    ],
  });

  const [deleteExternalCollaborator] = useDeleteExternalCollaboratorMutation({
    refetchQueries: [
      "OrganizationMembers",
      "OrganizationExternalCollaborators",
      "Organization",
    ],
  });

  const form = useForm({
    onSubmit: async () => {
      if (isOrganizationMember) {
        const result = await deleteOrganizationMember({
          variables: {
            input: {
              id: member.id,
            },
          },
        });

        if (!result.data?.deleteOrganizationMember.success) {
          const errors = result.data?.deleteOrganizationMember.errors || [];
          if (errors.includes(DeleteOrganizationMemberError.PermissionDenied)) {
            throw new Error(t("You are not authorized to perform this action"));
          }
          if (errors.includes(DeleteOrganizationMemberError.NotFound)) {
            throw new Error(t("Organization member not found"));
          }
          if (errors.includes(DeleteOrganizationMemberError.CannotDeleteSelf)) {
            throw new Error(
              t("You cannot remove yourself from the organization"),
            );
          }
          throw new Error(t("Failed to remove member"));
        }
        toast.success(t("Member removed"));
      } else {
        if (!organizationId) {
          throw new Error(t("Organization ID is required"));
        }

        const result = await deleteExternalCollaborator({
          variables: {
            input: {
              userId: member.user.id,
              organizationId: organizationId,
            },
          },
        });

        if (!result.data?.deleteExternalCollaborator.success) {
          const errors = result.data?.deleteExternalCollaborator.errors || [];
          if (
            errors.includes(DeleteExternalCollaboratorError.PermissionDenied)
          ) {
            throw new Error(t("You are not authorized to perform this action"));
          }
          if (errors.includes(DeleteExternalCollaboratorError.UserNotFound)) {
            throw new Error(t("User not found"));
          }
          if (
            errors.includes(
              DeleteExternalCollaboratorError.OrganizationNotFound,
            )
          ) {
            throw new Error(t("Organization not found"));
          }
          throw new Error(t("Failed to remove external collaborator"));
        }
        toast.success(t("External collaborator removed"));
      }

      client.cache.evict({ fieldName: "users" });
      client.cache.gc();
      onClose();
    },
    initialState: {},
  });

  return (
    <Dialog open={open} onClose={onClose} onSubmit={form.handleSubmit} centered>
      <Dialog.Title>
        {isOrganizationMember
          ? t("Remove Member")
          : t("Remove External Collaborator")}
      </Dialog.Title>
      <Dialog.Content>
        <p className="mb-4">
          {t("User:")} <b>{member.user.displayName}</b>
        </p>
        <p>
          {isOrganizationMember
            ? t(
                "Are you sure you want to remove this user from this organization and associated workspaces?",
              )
            : t(
                "Are you sure you want to remove this user from all workspaces in this organization?",
              )}
        </p>
        {form.submitError && (
          <div className="text-danger mt-3 text-sm">{form.submitError}</div>
        )}
      </Dialog.Content>
      <Dialog.Actions>
        <Button onClick={onClose} variant="white">
          {t("Cancel")}
        </Button>
        <Button type="submit" disabled={form.isSubmitting} variant="danger">
          {form.isSubmitting ? t("Removing...") : t("Remove")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
}

RemoveMemberDialog.fragments = {
  member: gql`
    fragment RemoveMemberDialog_member on OrganizationMember {
      id
      user {
        id
        displayName
      }
      ... on OrganizationMembership {
        role
      }
    }
  `,
};
