import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Field from "core/components/forms/Field";
import Textarea from "core/components/forms/Textarea";
import useCacheKey from "core/hooks/useCacheKey";
import useForm from "core/hooks/useForm";
import { useTranslation } from "next-i18next";
import { useEffect } from "react";
import { toast } from "react-toastify";
import {
  SavedQuery_SavedQueryFragment,
  useCreateSavedQueryMutation,
  useUpdateSavedQueryMutation,
} from "workspaces/features/SavedQueries/SavedQueries.generated";
import {
  createSavedQueryErrorMessage,
  updateSavedQueryErrorMessage,
} from "workspaces/features/SavedQueries/savedQueryErrors";

export type SaveQueryDialogMode = "create" | "edit-details";

type SaveQueryDialogProps = {
  open: boolean;
  onClose: () => void;
  mode: SaveQueryDialogMode;
  workspaceSlug: string;
  // The SQL to persist. Used in "create" mode; ignored when editing details.
  content?: string;
  // Prefill source: the query being edited ("edit-details"), or a query being
  // copied ("create" / save-as-new). Null for a brand-new query.
  savedQuery?: Pick<
    SavedQuery_SavedQueryFragment,
    "id" | "name" | "description"
  > | null;
  onSaved?: (savedQuery: SavedQuery_SavedQueryFragment) => void;
};

// max_length of SavedQuery.name on the backend.
const NAME_MAX_LENGTH = 255;

type Values = { name: string; description: string };

// Create / edit-details modal for a saved query. Visibility and slug are
// intentionally absent: the backend has no such concepts (all saved queries are
// workspace-visible, identified by id).
const SaveQueryDialog = ({
  open,
  onClose,
  mode,
  workspaceSlug,
  content,
  savedQuery,
  onSaved,
}: SaveQueryDialogProps) => {
  const { t } = useTranslation();
  const clearCache = useCacheKey("savedQueries");
  const [createSavedQuery] = useCreateSavedQueryMutation();
  const [updateSavedQuery] = useUpdateSavedQueryMutation();

  const form = useForm<Values>({
    getInitialState: () => ({
      name: savedQuery?.name ?? "",
      description: savedQuery?.description ?? "",
    }),
    validate: (values) => {
      const errors: any = {};
      const name = values.name?.trim();
      if (!name) {
        errors.name = t("Name is required");
      } else if (name.length > NAME_MAX_LENGTH) {
        errors.name = t("Name must be at most {{max}} characters", {
          max: NAME_MAX_LENGTH,
        });
      }
      return errors;
    },
    onSubmit: async (values) => {
      const name = values.name.trim();
      const description = values.description?.trim() ?? "";

      if (mode === "create") {
        const { data } = await createSavedQuery({
          variables: {
            input: { workspaceSlug, name, content: content ?? "", description },
          },
        });
        const result = data?.createSavedQuery;
        if (result?.success && result.savedQuery) {
          clearCache();
          toast.success(t("Query created"));
          onSaved?.(result.savedQuery);
          onClose();
        } else {
          throw new Error(createSavedQueryErrorMessage(result?.errors, t));
        }
      } else {
        if (!savedQuery) {
          return;
        }
        const { data } = await updateSavedQuery({
          variables: { input: { id: savedQuery.id, name, description } },
        });
        const result = data?.updateSavedQuery;
        if (result?.success && result.savedQuery) {
          clearCache();
          toast.success(t("Query updated"));
          onSaved?.(result.savedQuery);
          onClose();
        } else {
          throw new Error(updateSavedQueryErrorMessage(result?.errors, t));
        }
      }
    },
  });

  // Re-seed the form from the current props each time the dialog opens.
  useEffect(() => {
    if (open) {
      form.resetForm();
    }
  }, [open]);

  const title = mode === "create" ? t("Save query") : t("Edit details");
  const submitLabel = mode === "create" ? t("Save query") : t("Save");

  return (
    <Dialog open={open} onClose={onClose}>
      <form onSubmit={form.handleSubmit}>
        <Dialog.Title onClose={onClose}>{title}</Dialog.Title>
        <Dialog.Content className="space-y-4">
          <Field
            name="name"
            label={t("Name")}
            value={form.formData.name ?? ""}
            onChange={form.handleInputChange}
            required
            fullWidth
            autoFocus
            error={form.errors.name}
          />
          <Field name="description" label={t("Description")}>
            <Textarea
              name="description"
              value={form.formData.description ?? ""}
              onChange={form.handleInputChange}
              rows={3}
              placeholder={t("What does this query return? Any caveats?")}
            />
          </Field>
          {form.submitError && (
            <p className="text-sm text-red-600">{form.submitError}</p>
          )}
        </Dialog.Content>
        <Dialog.Actions>
          <Button onClick={onClose} variant="outlined">
            {t("Cancel")}
          </Button>
          <Button disabled={form.isSubmitting} type="submit">
            {submitLabel}
          </Button>
        </Dialog.Actions>
      </form>
    </Dialog>
  );
};

export default SaveQueryDialog;
