import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Field from "core/components/forms/Field";
import Textarea from "core/components/forms/Textarea";
import useForm from "core/hooks/useForm";
import { SavedQueryVisibility } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useEffect } from "react";
import { toast } from "react-toastify";
import { SavedQuery_SavedQueryFragment } from "workspaces/features/SavedQueries/SavedQueries.generated";
import SavedQueryVisibilityPicker from "workspaces/features/SavedQueries/SavedQueryVisibilityPicker";
import { useSavedQueryMutations } from "workspaces/features/SavedQueries/useSavedQueryMutations";

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
    "id" | "name" | "description" | "visibility" | "permissions"
  > | null;
  onSaved?: (savedQuery: SavedQuery_SavedQueryFragment) => void;
};

// max_length of SavedQuery.name on the backend.
const NAME_MAX_LENGTH = 255;

type Values = {
  name: string;
  description: string;
  visibility: SavedQueryVisibility;
};

// Create / edit-details modal for a saved query. Slug is intentionally absent:
// queries are identified by id on the backend.
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
  const { create, update } = useSavedQueryMutations();

  // An editor may edit a shared query without being allowed to unshare it. The
  // picker still shows the current state, just read-only.
  const canEditVisibility =
    mode === "create" || (savedQuery?.permissions.updateVisibility ?? false);

  const form = useForm<Values>({
    getInitialState: () => ({
      name: savedQuery?.name ?? "",
      description: savedQuery?.description ?? "",
      // Anything created here is a new query - including a save-as-new fork of a
      // shared one - so it starts private until its author shares it.
      visibility:
        mode === "create"
          ? SavedQueryVisibility.Private
          : (savedQuery?.visibility ?? SavedQueryVisibility.Private),
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

      if (mode === "edit-details" && !savedQuery) {
        return;
      }

      const res =
        mode === "create"
          ? await create({
              workspaceSlug,
              name,
              content: content ?? "",
              description,
              visibility: values.visibility,
            })
          : await update({
              id: savedQuery!.id,
              name,
              description,
              visibility: values.visibility,
            });

      if (res.ok) {
        toast.success(
          mode === "create" ? t("Query created") : t("Query updated"),
        );
        onSaved?.(res.savedQuery);
        onClose();
      } else {
        // Thrown so useForm surfaces it as a form-level submit error.
        throw new Error(res.message);
      }
    },
  });

  // The dialog stays mounted between opens (so its transitions can run), so the
  // form has to be re-seeded from the current props each time it opens. Keyed on
  // `open` alone on purpose: re-running this on a new `form` identity would wipe
  // whatever the user has typed.
  useEffect(() => {
    if (open) {
      form.resetForm();
    }
  }, [open]);

  const title = mode === "create" ? t("Save query") : t("Edit details");
  const submitLabel = mode === "create" ? t("Save query") : t("Save");

  return (
    <Dialog open={open} onClose={onClose} maxWidth="max-w-xl">
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
              rows={7}
              placeholder={t("What does this query return? Any caveats?")}
            />
          </Field>
          <Field name="visibility" label={t("Sharing")} showOptional={false}>
            <SavedQueryVisibilityPicker
              value={form.formData.visibility ?? SavedQueryVisibility.Private}
              onChange={(visibility) =>
                form.setFieldValue("visibility", visibility)
              }
              disabled={!canEditVisibility}
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
