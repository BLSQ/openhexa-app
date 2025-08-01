import { Trans, useTranslation } from "next-i18next";
import Dialog from "core/components/Dialog";
import Button from "core/components/Button";
import { useDeleteOrganizationMemberMutation } from "../OrganizationMembers.generated";
import { User, OrganizationMembership } from "graphql/types";

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

  const [deleteOrganizationMember, { loading }] =
    useDeleteOrganizationMemberMutation({
      refetchQueries: ["OrganizationMembers", "GetUsers", "Organization"],
    });

  const handleSubmit = async () => {
    deleteOrganizationMember({
      variables: {
        input: {
          id: member.id,
        },
      },
    }).then(() => onClose());
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
