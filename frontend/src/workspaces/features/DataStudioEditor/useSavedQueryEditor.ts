import useNavigationWarning from "core/hooks/useNavigationWarning";
import { useTranslation } from "next-i18next";
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
  const [savedQuery, setSavedQuery] =
    useState<SavedQuery_SavedQueryFragment | null>(initialSavedQuery ?? null);
  // Baseline the dirty check compares against; advances on each in-place save.
  const [baseline, setBaseline] = useState(initialSavedQuery?.content ?? "");
  const [dialog, setDialog] = useState<DialogState>(null);
  const { update, updating: saving } = useSavedQueryMutations();

  const canUpdate = savedQuery?.permissions.update ?? false;
  const isDirty = content !== baseline;

  // Only a loaded saved query is guarded. A buffer that was never saved has no
  // stored version to diverge from, so there is no "unsaved change" to describe;
  // warning about it would mean prompting on the way out of an editor the user
  // may simply have been experimenting in.
  //
  // Edits nobody can keep are not guarded either: a viewer who can neither update
  // this query nor save a copy has no Save control at all (see SaveQueryButton),
  // so warning them about losing changes only states the inevitable.
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
      // A new query was created (first save or save-as-new): open its page,
      // which remounts the editor against the freshly saved query. The buffer
      // still counts as dirty against the old baseline, hence the bypass.
      navigateWithoutWarning(dataStudioRoutes(workspaceSlug).query(sq.id));
    },
    [dialog, navigateWithoutWarning, workspaceSlug],
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
