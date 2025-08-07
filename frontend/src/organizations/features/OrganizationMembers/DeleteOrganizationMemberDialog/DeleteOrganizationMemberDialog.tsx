import { Trans, useTranslation } from "next-i18next";
import Dialog from "core/components/Dialog";
import Button from "core/components/Button";
import { useDeleteOrganizationMemberMutation } from "../OrganizationMembers.generated";
import { User, OrganizationMembership } from "graphql/types";
import { useApolloClient } from "@apollo/client";

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

  const [deleteOrganizationMember, { loading }] =
    useDeleteOrganizationMemberMutation({
      refetchQueries: ["OrganizationMembers", "Organization"]
    });

  const handleSubmit = async () => {
    deleteOrganizationMember({
      variables: {
        input: {
          id: member.id,
        },
      },
    }).then(() => {
      // Clear users cache so UserPicker gets fresh data, used instead of refetchQueries because the refetch is not happening when the dialog is closed
      client.cache.evict({ fieldName: "users" });
      client.cache.gc();
      onClose();
    });
  };

  return (
    <Dialog open={open} onClose={onClose} centered>
      <Dialog.Title>{t("Remove Member")}</Dialog.Title>
      <Dialog.Content>
        <Trans>
          <p>
            Are you sure you want to remove <b>{member.user.displayName}</b>{" "}
            from this organization and associated workspaces ?
          </p>
        </Trans>
      </Dialog.Content>
      <Dialog.Actions>
        <Button onClick={onClose} variant="white">
          {t("Cancel")}
        </Button>
        <Button onClick={handleSubmit} disabled={loading} variant="danger">
          {loading ? t("Removing...") : t("Remove")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
}
