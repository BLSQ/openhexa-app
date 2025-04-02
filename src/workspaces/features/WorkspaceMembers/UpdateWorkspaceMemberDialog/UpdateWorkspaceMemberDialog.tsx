import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Spinner from "core/components/Spinner";
import useForm from "core/hooks/useForm";
import { useEffect } from "react";
import { useTranslation } from "next-i18next";
import { useUpdateWorkspaceMemberMutation } from "workspaces/graphql/mutations.generated";
import { gql } from "@apollo/client";
import {
  UpdateWorkspaceMemberError,
  WorkspaceMembershipRole,
} from "graphql/types";
import { UpdateWorkspaceMember_WorkspaceMemberFragment } from "./UpdateWorkspaceMemberDialog.generated";
import Field from "core/components/forms/Field";
import SimpleSelect from "core/components/forms/SimpleSelect";

type UpdateWorkspaceMemberDialogProps = {
  onClose(): void;
  open: boolean;
  member: UpdateWorkspaceMember_WorkspaceMemberFragment;
};

type Form = {
  role: WorkspaceMembershipRole;
};

const UpdateWorkspaceMemberDialog = (
  props: UpdateWorkspaceMemberDialogProps,
) => {
  const { t } = useTranslation();
  const { open, onClose, member } = props;
  const [mutate] = useUpdateWorkspaceMemberMutation();

  const form = useForm<Form>({
    onSubmit: async (values) => {
      const { data } = await mutate({
        variables: {
          input: {
            membershipId: member.id,
            role: values.role,
          },
        },
      });
      if (!data?.updateWorkspaceMember) {
        throw new Error("Unknown error.");
      }
      if (
        data.updateWorkspaceMember.errors.includes(
          UpdateWorkspaceMemberError.PermissionDenied,
        )
      ) {
        throw new Error("You are not authorized to perform this action");
      }
      onClose();
    },
    initialState: {
      role: member.role,
    },
  });

  useEffect(() => {
    if (open) {
      form.resetForm();
    }
  }, [open, form]);

  return (
    <Dialog onSubmit={form.handleSubmit} open={open} onClose={onClose}>
      <Dialog.Title>{t("Edit member")}</Dialog.Title>
      <Dialog.Content className="space-y-4">
        <Field name="role" label={t("Role")} required>
          <SimpleSelect
            name="role"
            value={form.formData.role}
            onChange={form.handleInputChange}
            required
          >
            <option value={WorkspaceMembershipRole.Admin}>{t("Admin")}</option>
            <option value={WorkspaceMembershipRole.Editor}>
              {t("Editor")}
            </option>
            <option value={WorkspaceMembershipRole.Viewer}>
              {t("Viewer")}
            </option>
          </SimpleSelect>
        </Field>
        {form.submitError && (
          <div className="text-danger mt-3 text-sm">{form.submitError}</div>
        )}
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" onClick={onClose}>
          {t("Cancel")}
        </Button>
        <Button disabled={form.isSubmitting} type="submit">
          {form.isSubmitting && <Spinner size="xs" className="mr-1" />}
          {t("Save")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

UpdateWorkspaceMemberDialog.fragments = {
  member: gql`
    fragment UpdateWorkspaceMember_workspaceMember on WorkspaceMembership {
      id
      role
    }
  `,
};

export default UpdateWorkspaceMemberDialog;
