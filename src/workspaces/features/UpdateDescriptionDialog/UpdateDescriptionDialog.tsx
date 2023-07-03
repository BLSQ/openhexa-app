import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Spinner from "core/components/Spinner";
import useForm from "core/hooks/useForm";
import { useEffect } from "react";
import { useTranslation } from "react-i18next";
import Textarea from "core/components/forms/Textarea";
import { useUpdateWorkspaceMutation } from "workspaces/graphql/mutations.generated";
import { gql } from "@apollo/client";
import { UpdateWorkspaceError } from "graphql-types";
import { UpdateWorkspaceDescription_WorkspaceFragment } from "./UpdateDescriptionDialog.generated";

type UpdateDescriptionDialogProps = {
  onClose(): void;
  open: boolean;
  workspace: UpdateWorkspaceDescription_WorkspaceFragment;
};

type Form = {
  description: string;
};

const UpdateDescriptionDialog = (props: UpdateDescriptionDialogProps) => {
  const { t } = useTranslation();
  const { open, onClose, workspace } = props;
  const [mutate] = useUpdateWorkspaceMutation();
  const form = useForm<Form>({
    onSubmit: async (values) => {
      const { data } = await mutate({
        variables: {
          input: {
            slug: workspace.slug,
            description: values.description,
          },
        },
      });
      if (!data?.updateWorkspace) {
        throw new Error("Unknown error.");
      }
      if (
        data.updateWorkspace.errors.includes(
          UpdateWorkspaceError.PermissionDenied
        )
      ) {
        throw new Error("You are not authorized to perform this action");
      }
      onClose();
    },
    validate: (values) => {
      const errors = {} as any;

      if (!values.description) {
        errors.description = t("Type a description for the workspace");
      }
      return errors;
    },
    getInitialState() {
      return { description: workspace.description || "" };
    },
  });

  useEffect(() => {
    form.resetForm();
  }, [form, workspace]);

  useEffect(() => {
    if (!open) {
      form.resetForm();
    }
  }, [open, form]);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="max-w-5xl">
      <Dialog.Title>{t("Edit workspace's description")}</Dialog.Title>
      <form onSubmit={form.handleSubmit}>
        <Dialog.Content className="space-y-4">
          <Textarea
            name="description"
            required
            value={form.formData.description}
            onChange={form.handleInputChange}
            rows={20}
            data-testid="description"
          />
          {form.submitError && (
            <div className="text-danger mt-3 text-sm">{form.submitError}</div>
          )}
        </Dialog.Content>
        <Dialog.Actions>
          <Button variant="white" type="button" onClick={onClose}>
            {t("Cancel")}
          </Button>
          <Button disabled={form.isSubmitting} type="submit">
            {form.isSubmitting && <Spinner size="xs" className="mr-1" />}
            {t("Save")}
          </Button>
        </Dialog.Actions>
      </form>
    </Dialog>
  );
};

UpdateDescriptionDialog.fragments = {
  workspace: gql`
    fragment UpdateWorkspaceDescription_workspace on Workspace {
      slug
      description
    }
  `,
};

export default UpdateDescriptionDialog;
