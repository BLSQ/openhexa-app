import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Field from "core/components/forms/Field";
import Spinner from "core/components/Spinner";
import { useTranslation } from "next-i18next";
import { useInviteWorkspaceMemberMutation } from "workspaces/graphql/mutations.generated";
import useForm from "core/hooks/useForm";
import {
  InviteWorkspaceMembershipError,
  WorkspaceMembershipRole,
} from "graphql/types";
import Input from "core/components/forms/Input";
import SimpleSelect from "core/components/forms/SimpleSelect";
import { gql } from "@apollo/client";
import { InviteMemberWorkspace_WorkspaceFragment } from "./InviteMemberDialog.generated";
import useCacheKey from "core/hooks/useCacheKey";
import { useEffect } from "react";

type InviteMemberDialogProps = {
  onClose(): void;
  open: boolean;
  workspace: InviteMemberWorkspace_WorkspaceFragment;
};

type Form = {
  role: WorkspaceMembershipRole;
  email: string;
};

const InviteMemberDialog = (props: InviteMemberDialogProps) => {
  const { t } = useTranslation();
  const { open, onClose, workspace } = props;

  const [createWorkspaceMember] = useInviteWorkspaceMemberMutation();
  const clearCache = useCacheKey(["workspaces", workspace.slug]);

  const form = useForm<Form>({
    onSubmit: async (values) => {
      const { data } = await createWorkspaceMember({
        variables: {
          input: {
            role: values.role,
            workspaceSlug: workspace.slug,
            userEmail: values.email,
          },
        },
      });

      if (!data?.inviteWorkspaceMember) {
        throw new Error("Unknown error.");
      }

      if (
        data.inviteWorkspaceMember.errors.includes(
          InviteWorkspaceMembershipError.AlreadyExists,
        )
      ) {
        throw new Error("User already invited to this workspace.");
      }

      if (
        data.inviteWorkspaceMember.errors.includes(
          InviteWorkspaceMembershipError.UserNotFound,
        )
      ) {
        throw new Error("No user matching this email address.");
      }
      if (
        data.inviteWorkspaceMember.errors.includes(
          InviteWorkspaceMembershipError.PermissionDenied,
        )
      ) {
        throw new Error("You are not authorized to perform this action");
      }
      clearCache();
      handleClose();
    },
    initialState: { role: WorkspaceMembershipRole.Viewer, email: "" },
    validate: (values) => {
      const errors = {} as any;
      if (!values.email) {
        errors.email = t("Email address is mandatory");
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
      <Dialog.Title>{t("Invite member")}</Dialog.Title>
      <Dialog.Content className="space-y-4">
        <Field name="email" label={t("Email address")} type="email" required>
          <Input
            placeholder={t("sabrina@bluesquarehub.com")}
            name="email"
            type="email"
            autoComplete="email"
            required
            fullWidth
            value={form.formData.email}
            onChange={form.handleInputChange}
            error={form.touched.email && form.errors.email}
          />
        </Field>
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
        <Button onClick={handleClose} variant="white">
          {t("Cancel")}
        </Button>
        <Button
          type="submit"
          className="space-x-2"
          disabled={form.isSubmitting}
        >
          {form.isSubmitting && <Spinner size="xs" className="mr-1" />}
          {t("Invite")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

InviteMemberDialog.fragments = {
  workspace: gql`
    fragment InviteMemberWorkspace_workspace on Workspace {
      slug
      name
    }
  `,
};

export default InviteMemberDialog;
