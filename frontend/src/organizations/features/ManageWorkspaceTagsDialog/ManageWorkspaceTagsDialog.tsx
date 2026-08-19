import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Field from "core/components/forms/Field";
import Select from "core/components/forms/Select";
import Spinner from "core/components/Spinner";
import useCacheKey from "core/hooks/useCacheKey";
import useForm from "core/hooks/useForm";
import { SetWorkspaceTagsError } from "graphql/types";
import { useTranslation } from "next-i18next";
import { toast } from "react-toastify";
import { useSetWorkspaceTagsMutation } from "./ManageWorkspaceTagsDialog.generated";

type WorkspaceForDialog = {
  slug: string;
  name: string;
  tags: { name: string }[];
};

type ManageWorkspaceTagsDialogProps = {
  open: boolean;
  onClose(): void;
  workspace: WorkspaceForDialog;
  organizationId: string;
  availableTags: string[];
};

type Form = {
  tags: string[];
};

const ManageWorkspaceTagsDialog = ({
  open,
  onClose,
  workspace,
  organizationId,
  availableTags,
}: ManageWorkspaceTagsDialogProps) => {
  const { t } = useTranslation();
  const [setWorkspaceTags] = useSetWorkspaceTagsMutation({
    refetchQueries: ["OrganizationWorkspaces"],
  });
  const clearCache = useCacheKey(["organization", organizationId]);

  const form = useForm<Form>({
    onSubmit: async (values) => {
      const result = await setWorkspaceTags({
        variables: { input: { slug: workspace.slug, tags: values.tags } },
      });

      if (!result.data?.setWorkspaceTags.success) {
        const errors = result.data?.setWorkspaceTags.errors || [];
        if (errors.includes(SetWorkspaceTagsError.PermissionDenied)) {
          throw new Error(t("You are not authorized to perform this action"));
        }
        if (errors.includes(SetWorkspaceTagsError.InvalidTag)) {
          throw new Error(
            t("One of the tags contains no letters or numbers to use."),
          );
        }
        if (errors.includes(SetWorkspaceTagsError.NotFound)) {
          throw new Error(t("Workspace not found"));
        }
        throw new Error(t("Failed to update the tags of the workspace"));
      }

      toast.success(t("Tags updated!"));
      clearCache();
      onClose();
    },
    initialState: { tags: workspace.tags.map((tag) => tag.name) },
  });

  return (
    <Dialog
      open={open}
      onClose={onClose}
      onSubmit={form.handleSubmit}
      maxWidth="max-w-lg"
    >
      <Dialog.Title>{t("Manage tags")}</Dialog.Title>
      <Dialog.Content className="space-y-4">
        <p className="text-sm text-gray-600">
          {t(
            "Tag {{name}} to organize and filter the workspaces of your organization.",
            {
              name: workspace.name,
            },
          )}
        </p>

        <Field name="tags" label={t("Tags")}>
          <Select
            multiple
            withPortal
            options={availableTags}
            value={form.formData.tags ?? []}
            onChange={(value) => form.setFieldValue("tags", value as string[])}
            getOptionLabel={(option) => option}
            onCreate={(query) =>
              form.setFieldValue("tags", [...(form.formData.tags ?? []), query])
            }
            addLabel={t("Create tag")}
            placeholder={t("Select or create tags...")}
          />
        </Field>

        <p className="text-sm text-gray-500">
          {t(
            'Tags are normalized to lowercase words separated by hyphens, so "Project Alpha" is saved as "project-alpha".',
          )}
        </p>

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
          {t("Save")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

export default ManageWorkspaceTagsDialog;
