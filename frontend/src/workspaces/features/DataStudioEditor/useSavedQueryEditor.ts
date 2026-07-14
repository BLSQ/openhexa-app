import useCacheKey from "core/hooks/useCacheKey";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useCallback, useState } from "react";
import { toast } from "react-toastify";
import {
  SavedQuery_SavedQueryFragment,
  useUpdateSavedQueryMutation,
} from "workspaces/features/SavedQueries/SavedQueries.generated";
import { updateSavedQueryErrorMessage } from "workspaces/features/SavedQueries/savedQueryErrors";

type DialogState = { mode: "create" | "edit-details" } | null;

type UseSavedQueryEditorArgs = {
  workspaceSlug: string;
  content: string;
  initialSavedQuery?: SavedQuery_SavedQueryFragment | null;
};

// Owns the write-path state machine for the SQL editor: whether the current
// buffer maps to a saved query, whether it has unsaved changes, and the
// save / save-as-new / edit-details actions plus the dialog they drive. Kept
// separate from run/export orchestration so each concern stays testable.
export const useSavedQueryEditor = ({
  workspaceSlug,
  content,
  initialSavedQuery,
}: UseSavedQueryEditorArgs) => {
  const { t } = useTranslation();
  const router = useRouter();
  const [savedQuery, setSavedQuery] =
    useState<SavedQuery_SavedQueryFragment | null>(initialSavedQuery ?? null);
  // Baseline the dirty check compares against; advances on each in-place save.
  const [baseline, setBaseline] = useState(initialSavedQuery?.content ?? "");
  const [dialog, setDialog] = useState<DialogState>(null);
  const [updateSavedQuery, { loading: saving }] = useUpdateSavedQueryMutation();
  const clearCache = useCacheKey("savedQueries");

  const canUpdate = savedQuery?.permissions.update ?? false;
  const isDirty = content !== baseline;

  // Primary Save: create a brand-new query (via the dialog), or update the
  // content of the loaded query in place.
  const save = useCallback(async () => {
    if (!savedQuery) {
      setDialog({ mode: "create" });
      return;
    }
    if (!canUpdate || saving) {
      return;
    }
    try {
      const { data } = await updateSavedQuery({
        variables: { input: { id: savedQuery.id, content } },
      });
      const result = data?.updateSavedQuery;
      if (result?.success && result.savedQuery) {
        setSavedQuery(result.savedQuery);
        setBaseline(content);
        clearCache();
        toast.success(t("Query saved"));
      } else {
        toast.error(updateSavedQueryErrorMessage(result?.errors, t));
      }
    } catch (err: any) {
      toast.error(err.message);
    }
  }, [savedQuery, canUpdate, saving, content, updateSavedQuery, clearCache, t]);

  const saveAsNew = useCallback(() => setDialog({ mode: "create" }), []);
  const editDetails = useCallback(
    () => setDialog({ mode: "edit-details" }),
    [],
  );
  const closeDialog = useCallback(() => setDialog(null), []);

  const onDialogSaved = useCallback(
    (sq: SavedQuery_SavedQueryFragment) => {
      if (dialog?.mode === "edit-details") {
        // Only metadata changed; the content baseline is untouched.
        setSavedQuery(sq);
      } else {
        // A new query was created (first save or save-as-new): open its page,
        // which remounts the editor against the freshly saved query.
        router.push(
          `/workspaces/${encodeURIComponent(
            workspaceSlug,
          )}/data-studio/queries/${encodeURIComponent(sq.id)}`,
        );
      }
    },
    [dialog, router, workspaceSlug],
  );

  return {
    savedQuery,
    isDirty,
    saving,
    canUpdate,
    dialog,
    save,
    saveAsNew,
    editDetails,
    closeDialog,
    onDialogSaved,
  };
};
