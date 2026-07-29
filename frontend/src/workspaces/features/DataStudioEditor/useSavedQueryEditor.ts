import useNavigationWarning from "core/hooks/useNavigationWarning";
import { useTranslation } from "next-i18next";
import { useCallback, useState } from "react";
import { toast } from "react-toastify";
import { SavedQuery_SavedQueryFragment } from "workspaces/features/SavedQueries/SavedQueries.generated";
import { useSavedQueryMutations } from "workspaces/features/SavedQueries/useSavedQueryMutations";
import { dataStudioRoutes } from "workspaces/helpers/dataStudio";
import { clearScratch } from "./dataStudioScratch";

type DialogState = { mode: "create" | "edit-details" } | null;

type UseSavedQueryEditorArgs = {
  userId?: string;
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
  userId,
  workspaceSlug,
  content,
  initialSavedQuery,
  canCreate = false,
}: UseSavedQueryEditorArgs) => {
  const { t } = useTranslation();
  const [savedQuery, setSavedQuery] =
    useState<SavedQuery_SavedQueryFragment | null>(initialSavedQuery ?? null);
  // Baseline the dirty check compares against; advances on each in-place save.
  const [baseline, setBaseline] = useState(initialSavedQuery?.content ?? "");
  const [dialog, setDialog] = useState<DialogState>(null);
  const { update, updating: saving } = useSavedQueryMutations();

  const canUpdate = savedQuery?.permissions.update ?? false;
  const isDirty = content !== baseline;

  // Edits to an unsaved scratch buffer are not guarded: they survive navigation
  // on their own (see useQueryBuffer), so a prompt would be pure friction.
  //
  // Neither are edits nobody can keep: a viewer who can neither update this
  // query nor save a copy has no Save control at all (see SaveQueryButton), so
  // warning them about losing changes only states the inevitable.
  const canPersist = canUpdate || canCreate;
  const { navigateWithoutWarning } = useNavigationWarning({
    enabled: Boolean(savedQuery) && isDirty && canPersist,
    message: savedQuery
      ? t(
          'You have unsaved changes to "{{name}}". If you leave this page, they will be lost.',
          { name: savedQuery.name },
        )
      : undefined,
  });

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
        return;
      }
      // The scratch draft has become a saved query, so it no longer needs to be
      // held. Save-as-new leaves it alone: the draft belongs to the unsaved
      // editor, not to the query being copied.
      if (!savedQuery && userId) {
        clearScratch({ userId, workspaceSlug });
      }
      // A new query was created (first save or save-as-new): open its page,
      // which remounts the editor against the freshly saved query. The buffer
      // still counts as dirty against the old baseline, hence the bypass.
      navigateWithoutWarning(dataStudioRoutes(workspaceSlug).query(sq.id));
    },
    [dialog, savedQuery, navigateWithoutWarning, userId, workspaceSlug],
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
