import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Field from "core/components/forms/Field";
import Input from "core/components/forms/Input";
import Spinner from "core/components/Spinner";
import { useTranslation } from "next-i18next";
import useForm from "core/hooks/useForm";
import {
  AddOrganizationMemberError,
  OrganizationMembershipRole,
} from "graphql/types";
import SimpleSelect from "core/components/forms/SimpleSelect";
import useCacheKey from "core/hooks/useCacheKey";
import { useEffect } from "react";
import { useAddOrganizationMemberMutation } from "../OrganizationMembers.generated";

type AddOrganizationMemberDialogProps = {
  onClose(): void;
  open: boolean;
  organizationId: string;
};

type Form = {
  userEmail: string;
  role: OrganizationMembershipRole;
};

const AddOrganizationMemberDialog = (
  props: AddOrganizationMemberDialogProps,
) => {
  const { t } = useTranslation();
  const { open, onClose, organizationId } = props;

  const [addOrganizationMember] = useAddOrganizationMemberMutation({
    refetchQueries: ["OrganizationMembers"],
  });

  const clearCache = useCacheKey(["organization", organizationId]);

  const form = useForm<Form>({
    onSubmit: async (values) => {
      const { data } = await addOrganizationMember({
        variables: {
          input: {
            userEmail: values.userEmail,
            organizationId,
            role: values.role,
          },
        },
      });

      if (!data?.addOrganizationMember) {
        throw new Error("Unknown error.");
      }

      if (
        data.addOrganizationMember.errors.includes(
          AddOrganizationMemberError.PermissionDenied,
        )
      ) {
        throw new Error("You are not authorized to perform this action");
      }

      if (data.addOrganizationMember.errors.length > 0) {
        throw new Error("An error occurred while adding the member.");
      }

      clearCache();
      handleClose();
    },
    initialState: {
      userEmail: "",
      role: OrganizationMembershipRole.Member,
    },
    validate: (values) => {
      const errors = {} as any;
      if (!values.userEmail || !values.userEmail.includes("@")) {
        errors.userEmail = t("Valid email address is required");
      }
      if (!values.role) {
        errors.role = t("Member role is mandatory");
      }
      return errors;
    },
  });

  const handleClose = () => {
    onClose();
  };

  useEffect(() => {
    if (open) {
      form.resetForm();
    }
  }, [open, form]);

  return (
    <Dialog open={open} onClose={handleClose} onSubmit={form.handleSubmit}>
      <Dialog.Title>{t("Add Organization Member")}</Dialog.Title>
      <Dialog.Content className="space-y-4">
        <Field
          name="userEmail"
          label={t("Email address")}
          type="email"
          required
        >
          <Input
            name="userEmail"
            type="email"
            value={form.formData.userEmail}
            onChange={form.handleInputChange}
            placeholder={t("Enter user email address")}
            required
          />
        </Field>
        <Field name="role" label={t("Organization Role")} required>
          <SimpleSelect
            name="role"
            value={form.formData.role}
            onChange={form.handleInputChange}
            required
          >
            <option value={OrganizationMembershipRole.Member}>
              {t("Member")}
            </option>
            <option value={OrganizationMembershipRole.Admin}>
              {t("Admin")}
            </option>
            <option value={OrganizationMembershipRole.Owner}>
              {t("Owner")}
            </option>
          </SimpleSelect>
        </Field>

        {form.submitError && (
          <div className="text-danger mt-3 text-sm">{form.submitError}</div>
        )}
      </Dialog.Content>
      <Dialog.Actions>
        <Button onClick={handleClose} variant="white">
          {t("Cancel")}
        </Button>
        <Button
          type="submit"
          className="space-x-2"
          disabled={form.isSubmitting}
        >
          {form.isSubmitting && <Spinner size="xs" className="mr-1" />}
          {t("Add Member")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

export default AddOrganizationMemberDialog;
