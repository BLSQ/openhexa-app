import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useCallback, useState } from "react";
import { toast } from "react-toastify";
import { SavedQuery_SavedQueryFragment } from "workspaces/features/SavedQueries/SavedQueries.generated";
import { useSavedQueryMutations } from "workspaces/features/SavedQueries/useSavedQueryMutations";
import { dataStudioRoutes } from "workspaces/helpers/dataStudio";

type DialogState = { mode: "create" | "edit-details" } | null;

type UseSavedQueryEditorArgs = {
  workspaceSlug: string;
  content: string;
  initialSavedQuery?: SavedQuery_SavedQueryFragment | null;
  canCreate?: boolean;
};

// Owns the write-path state machine for the SQL editor: whether the current
// buffer maps to a saved query, whether it has unsaved changes, and the
// save / save-as-new / edit-details actions plus the dialog they drive. Kept
// separate from run/export orchestration so each concern stays testable.
export const useSavedQueryEditor = ({
  workspaceSlug,
  content,
  initialSavedQuery,
  canCreate = false,
}: UseSavedQueryEditorArgs) => {
  const { t } = useTranslation();
  const router = useRouter();
  const [savedQuery, setSavedQuery] =
    useState<SavedQuery_SavedQueryFragment | null>(initialSavedQuery ?? null);
  // Baseline the dirty check compares against; advances on each in-place save.
  const [baseline, setBaseline] = useState(initialSavedQuery?.content ?? "");
  const [dialog, setDialog] = useState<DialogState>(null);
  const { update, updating: saving } = useSavedQueryMutations();

  const canUpdate = savedQuery?.permissions.update ?? false;
  const isDirty = content !== baseline;
  const hasContent = Boolean(content.trim());

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
      const res = await update({ id: savedQuery.id, content });
      if (res.ok) {
        setSavedQuery(res.savedQuery);
        setBaseline(content);
        toast.success(t("Query saved"));
      } else {
        toast.error(res.message);
      }
    } catch (err: any) {
      toast.error(err.message);
    }
  }, [savedQuery, canUpdate, saving, content, update, t]);

  const saveAsNew = useCallback(() => setDialog({ mode: "create" }), []);

  // The single "save now" command, for callers that have no button state to lean
  // on (the ⌘S/Ctrl+S shortcut): resolves what saving means in the current state
  // and dispatches to the actions above. Every state with nothing to persist
  // falls through silently, mirroring the disabled Save button.
  const commit = useCallback(() => {
    if (!hasContent || saving || dialog) {
      return;
    }
    if (!savedQuery) {
      if (canCreate) {
        save();
      }
      return;
    }
    if (!canUpdate) {
      if (canCreate) {
        saveAsNew();
      }
      return;
    }
    if (isDirty) {
      save();
    }
  }, [
    hasContent,
    saving,
    dialog,
    savedQuery,
    canCreate,
    canUpdate,
    isDirty,
    save,
    saveAsNew,
  ]);

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
        router.push(dataStudioRoutes(workspaceSlug).query(sq.id));
      }
    },
    [dialog, router, workspaceSlug],
  );

  return {
    savedQuery,
    isDirty,
    hasContent,
    saving,
    canUpdate,
    dialog,
    save,
    saveAsNew,
    commit,
    editDetails,
    closeDialog,
    onDialogSaved,
  };
};
