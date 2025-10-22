import { Trans, useTranslation } from "next-i18next";
import Dialog from "core/components/Dialog";
import Button from "core/components/Button";
import {
  User,
  OrganizationMembership,
  DeleteOrganizationMemberError,
} from "graphql/types";
import { useApolloClient } from "@apollo/client/react";
import useForm from "core/hooks/useForm";
import { useMutation } from "@apollo/client/react";
import { graphql } from "graphql/gql";

const DeleteOrganizationMemberDoc = graphql(`
mutation DeleteOrganizationMember($input: DeleteOrganizationMemberInput!) {
  deleteOrganizationMember(input: $input) {
    success
    errors
  }
}
`);

type OrganizationMember = Pick<OrganizationMembership, "id" | "role"> & {
  user: Pick<User, "id" | "displayName">;
};

interface DeleteOrganizationMemberDialogProps {
  open: boolean;
  onClose: () => void;
  member: OrganizationMember;
}

export default function DeleteOrganizationMemberDialog({
  open,
  onClose,
  member,
}: DeleteOrganizationMemberDialogProps) {
  const { t } = useTranslation();
  const client = useApolloClient();

  const [deleteOrganizationMember] = useMutation(DeleteOrganizationMemberDoc, {
    refetchQueries: ["OrganizationMembers", "Organization"],
  });

  const form = useForm({
    onSubmit: async () => {
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

      // Clear users cache so UserPicker gets fresh data, used instead of refetchQueries because the refetch is not happening when the dialog is closed
      client.cache.evict({ fieldName: "users" });
      client.cache.gc();
      onClose();
    },
    initialState: {},
  });

  return (
    <Dialog open={open} onClose={onClose} onSubmit={form.handleSubmit} centered>
      <Dialog.Title>{t("Remove Member")}</Dialog.Title>
      <Dialog.Content>
        <Trans>
          <p>
            Are you sure you want to remove <b>{member.user.displayName}</b>{" "}
            from this organization and associated workspaces ?
          </p>
        </Trans>
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
