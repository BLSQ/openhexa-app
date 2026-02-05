import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Field from "core/components/forms/Field";
import Spinner from "core/components/Spinner";
import { useTranslation } from "next-i18next";
import useForm from "core/hooks/useForm";
import {
  OrganizationMembershipRole,
  ConvertExternalCollaboratorToMemberError,
} from "graphql/types";
import SimpleSelect from "core/components/forms/SimpleSelect";
import useCacheKey from "core/hooks/useCacheKey";
import { gql } from "@apollo/client";
import { toast } from "react-toastify";
import { useConvertExternalCollaboratorToMemberMutation } from "organizations/features/OrganizationExternalCollaborators/OrganizationExternalCollaborators.generated";
import { formatOrganizationMembershipRole } from "organizations/helpers/organization";
import { ConvertToMemberDialog_CollaboratorFragment } from "./ConvertToMemberDialog.generated";

type OrganizationForDialog = {
  id: string;
  permissions: {
    manageOwners: boolean;
  };
};

type ConvertToMemberDialogProps = {
  onClose(): void;
  open: boolean;
  collaborator: ConvertToMemberDialog_CollaboratorFragment;
  organization: OrganizationForDialog;
};

type Form = {
  role: OrganizationMembershipRole;
};

const ConvertToMemberDialog = (props: ConvertToMemberDialogProps) => {
  const { t } = useTranslation();
  const { open, onClose, collaborator, organization } = props;

  const [convertToMember] = useConvertExternalCollaboratorToMemberMutation({
    refetchQueries: [
      "OrganizationMembers",
      "OrganizationExternalCollaborators",
      "Organization",
    ],
  });

  const clearCache = useCacheKey(["organization", organization.id]);

  const form = useForm<Form>({
    onSubmit: async (values) => {
      const result = await convertToMember({
        variables: {
          input: {
            userId: collaborator.user.id,
            organizationId: organization.id,
            role: values.role,
          },
        },
      });

      if (!result.data?.convertExternalCollaboratorToMember.success) {
        const errors =
          result.data?.convertExternalCollaboratorToMember.errors || [];
        if (
          errors.includes(
            ConvertExternalCollaboratorToMemberError.PermissionDenied,
          )
        ) {
          throw new Error(t("You are not authorized to perform this action"));
        }
        if (
          errors.includes(
            ConvertExternalCollaboratorToMemberError.UserNotFound,
          )
        ) {
          throw new Error(t("User not found"));
        }
        if (
          errors.includes(
            ConvertExternalCollaboratorToMemberError.OrganizationNotFound,
          )
        ) {
          throw new Error(t("Organization not found"));
        }
        if (
          errors.includes(
            ConvertExternalCollaboratorToMemberError.NotExternalCollaborator,
          )
        ) {
          throw new Error(
            t(
              "This user is not an external collaborator or is already an organization member",
            ),
          );
        }
        if (
          errors.includes(
            ConvertExternalCollaboratorToMemberError.UsersLimitReached,
          )
        ) {
          throw new Error(t("Organization has reached its user limit"));
        }
        throw new Error(t("Failed to convert external collaborator to member"));
      }

      toast.success(t("Converted to member!"), { autoClose: 2000 });
      clearCache();
      onClose();
    },
    initialState: {
      role: OrganizationMembershipRole.Member,
    },
  });

  return (
    <Dialog
      open={open}
      onClose={onClose}
      onSubmit={form.handleSubmit}
      maxWidth="max-w-lg"
    >
      <Dialog.Title>{t("Convert to Organization Member")}</Dialog.Title>
      <Dialog.Content className="space-y-4">
        <p className="text-sm text-gray-600">
          {t("Converting")} <b>{collaborator.user.displayName}</b> (
          {collaborator.user.email}) {t("to organization member.")}
        </p>

        <p className="text-sm text-gray-500">
          {t("Existing workspace permissions will be preserved.")}
        </p>

        <Field name="role" label={t("Organization Role")} required>
          <SimpleSelect
            id="role"
            name="role"
            value={form.formData.role}
            onChange={form.handleInputChange}
            required
          >
            {Object.values(OrganizationMembershipRole)
              .filter((role) => {
                if (role === OrganizationMembershipRole.Owner) {
                  return organization.permissions.manageOwners;
                }
                return true;
              })
              .map((role) => (
                <option key={role} value={role}>
                  {formatOrganizationMembershipRole(role)}
                </option>
              ))}
          </SimpleSelect>
        </Field>

        {form.submitError && (
          <div className="text-danger mt-3 text-sm">{form.submitError}</div>
        )}
      </Dialog.Content>
      <Dialog.Actions>
        <Button onClick={onClose} variant="white">
          {t("Cancel")}
        </Button>
        <Button type="submit" disabled={form.isSubmitting}>
          {form.isSubmitting && <Spinner size="xs" className="mr-1" />}
          {t("Convert to member")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

ConvertToMemberDialog.fragments = {
  collaborator: gql`
    fragment ConvertToMemberDialog_collaborator on ExternalCollaborator {
      id
      user {
        id
        displayName
        email
      }
    }
  `,
};

export default ConvertToMemberDialog;
