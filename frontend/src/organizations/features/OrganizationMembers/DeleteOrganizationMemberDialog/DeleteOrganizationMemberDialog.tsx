import { useTranslation } from "next-i18next";
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

  const [deleteOrganizationMember, { loading }] = useDeleteOrganizationMemberMutation({
    onCompleted: (data) => {
      if (data.deleteOrganizationMember.success) {
        onClose();
      }
    },
    refetchQueries: ["OrganizationMembers"],
  });

  const handleSubmit = async () => {
    await deleteOrganizationMember({
      variables: {
        input: {
          id: member.id,
        },
      },
    });
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      centered
      maxWidth="max-w-md"
    >
      <Dialog.Title>{t("Remove Organization Member")}</Dialog.Title>
      <Dialog.Content>
        <p className="text-sm text-gray-600">
          {t("Are you sure you want to remove {{name}} from this organization?", {
            name: member.user.displayName,
          })}
        </p>
      </Dialog.Content>
      <Dialog.Actions>
        <Button onClick={onClose} variant="white">
          {t("Cancel")}
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={loading}
          variant="danger"
        >
          {loading ? t("Removing...") : t("Remove")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
}