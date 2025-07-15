import { useTranslation } from "next-i18next";
import { useState } from "react";
import Dialog from "core/components/Dialog";
import Field from "core/components/forms/Field";
import Select from "core/components/forms/Select";
import Button from "core/components/Button";
import { useUpdateOrganizationMemberMutation } from "../OrganizationMembers.generated";
import { User, OrganizationMembership, OrganizationMembershipRole } from "graphql/types";
import { formatOrganizationMembershipRole } from "organizations/helpers/organization";

type OrganizationMember = Pick<OrganizationMembership, "id" | "role"> & {
  user: Pick<User, "id" | "displayName">;
};

interface UpdateOrganizationMemberDialogProps {
  open: boolean;
  onClose: () => void;
  member: OrganizationMember;
}

export default function UpdateOrganizationMemberDialog({
  open,
  onClose,
  member,
}: UpdateOrganizationMemberDialogProps) {
  const { t } = useTranslation();
  const [role, setRole] = useState<OrganizationMembershipRole>(member.role);

  const [updateOrganizationMember, { loading }] = useUpdateOrganizationMemberMutation({
    onCompleted: (data) => {
      if (data.updateOrganizationMember.success) {
        onClose();
      }
    },
    refetchQueries: ["OrganizationMembers"],
  });

  const handleSubmit = async () => {
    await updateOrganizationMember({
      variables: {
        input: {
          id: member.id,
          role,
        },
      },
    });
  };

  const roleOptions = Object.values(OrganizationMembershipRole).map((roleValue) => ({
    value: roleValue,
    label: formatOrganizationMembershipRole(roleValue),
  }));

  const handleRoleChange = (selectedOption: { value: OrganizationMembershipRole; label: string } | null) => {
    if (selectedOption) {
      setRole(selectedOption.value);
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      centered
      maxWidth="max-w-md"
    >
      <Dialog.Title>{t("Update Organization Member")}</Dialog.Title>
      <Dialog.Content>
        <div className="space-y-4">
          <div>
            <p className="text-sm text-gray-600 mb-2">
              {t("Updating role for {{name}}", {
                name: member.user.displayName,
              })}
            </p>
          </div>
          <Field name="role" label={t("Role")} required>
            <Select
              value={roleOptions.find(option => option.value === role)}
              onChange={handleRoleChange}
              options={roleOptions}
              getOptionLabel={(option) => option?.label || ""}
              placeholder={t("Select role")}
            />
          </Field>
        </div>
      </Dialog.Content>
      <Dialog.Actions>
        <Button onClick={onClose} variant="white">
          {t("Cancel")}
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={loading || role === member.role}
          variant="primary"
        >
          {loading ? t("Updating...") : t("Update")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
}