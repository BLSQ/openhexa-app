import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Field from "core/components/forms/Field";
import Switch from "core/components/Switch";
import Textarea from "core/components/forms/Textarea";
import useForm from "core/hooks/useForm";
import { useTranslation } from "next-i18next";
import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import { SavedQuery_SavedQueryFragment } from "workspaces/features/SavedQueries/SavedQueries.generated";
import { useSavedQueryMutations } from "workspaces/features/SavedQueries/useSavedQueryMutations";
import SavedQueryParametersEditor from "./SavedQueryParametersEditor";
import SavedQueryPublicShare from "./SavedQueryPublicShare";
import {
  SavedQueryParameter,
  cleanParameters,
  parseParameters,
} from "./savedQueryParameters";

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
    | "id"
    | "name"
    | "slug"
    | "description"
    | "isPublic"
    | "parameters"
    | "permissions"
  > | null;
  onSaved?: (savedQuery: SavedQuery_SavedQueryFragment) => void;
};

// max_length of SavedQuery.name on the backend.
const NAME_MAX_LENGTH = 255;

type Values = { name: string; description: string };

// Create / edit-details modal for a saved query. Also edits the parameter spec
// (both modes) and, for admins editing an existing query, the public flag.
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

  const [parameters, setParameters] = useState<SavedQueryParameter[]>([]);
  const [isPublic, setIsPublic] = useState(false);

  // Only offer the public toggle when editing an existing query the user is
  // allowed to publish (an admin-only permission). New queries start private.
  const canTogglePublic =
    mode === "edit-details" && Boolean(savedQuery?.permissions.publish);

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
      const cleanedParameters = cleanParameters(parameters);

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
              parameters: cleanedParameters,
            })
          : await update({
              id: savedQuery!.id,
              name,
              description,
              parameters: cleanedParameters,
              ...(canTogglePublic ? { isPublic } : {}),
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

  // Re-seed the form (and the non-useForm state) from the current props each
  // time the dialog opens.
  useEffect(() => {
    if (open) {
      form.resetForm();
      setParameters(parseParameters(savedQuery?.parameters));
      setIsPublic(Boolean(savedQuery?.isPublic));
    }
  }, [open]);

  const title = mode === "create" ? t("Save query") : t("Edit details");
  const submitLabel = mode === "create" ? t("Save query") : t("Save");

  return (
    <Dialog open={open} onClose={onClose} maxWidth="max-w-2xl">
      <form onSubmit={form.handleSubmit}>
        <Dialog.Title onClose={onClose}>{title}</Dialog.Title>
        <Dialog.Content className="max-h-[70vh] space-y-4 overflow-y-auto">
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
              rows={4}
              placeholder={t("What does this query return? Any caveats?")}
            />
          </Field>

          <Field name="parameters" label={t("Parameters")}>
            <SavedQueryParametersEditor
              value={parameters}
              onChange={setParameters}
            />
          </Field>

          {canTogglePublic && (
            <div className="flex items-center justify-between rounded-md border border-gray-200 p-3">
              <div>
                <p className="text-sm font-medium text-gray-800">
                  {t("Public")}
                </p>
                <p className="text-xs text-gray-500">
                  {t("Allow anyone to run this query anonymously via the API.")}
                </p>
              </div>
              <Switch checked={isPublic} onChange={setIsPublic} />
            </div>
          )}

          {savedQuery?.isPublic && savedQuery.slug && (
            <SavedQueryPublicShare
              workspaceSlug={workspaceSlug}
              slug={savedQuery.slug}
              parameters={parseParameters(savedQuery.parameters)}
            />
          )}

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
