import { SavedQueryVisibility } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useCallback, useState } from "react";
import { toast } from "react-toastify";
import { SaveQueryDialogMode } from "workspaces/features/SavedQueries/SaveQueryDialog";
import { SavedQuery_SavedQueryFragment } from "workspaces/features/SavedQueries/SavedQueries.generated";
import { useSavedQueryMutations } from "workspaces/features/SavedQueries/useSavedQueryMutations";
import { dataStudioRoutes } from "workspaces/helpers/dataStudio";

// The dialog stays mounted and is toggled through `open` (so Headless UI can run
// its enter/leave transitions), hence the mode is kept alongside it: it must
// survive the leave transition or the title would change while fading out.
type DialogState = { open: boolean; mode: SaveQueryDialogMode };

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
  const [dialog, setDialog] = useState<DialogState>({
    open: false,
    mode: "create",
  });
  const { update, updating: saving } = useSavedQueryMutations();

  const canUpdate = savedQuery?.permissions.update ?? false;
  const canUpdateVisibility = savedQuery?.permissions.updateVisibility ?? false;
  const isDirty = content !== baseline;

  // Primary Save: create a brand-new query (via the dialog), or update the
  // content of the loaded query in place.
  const save = useCallback(async () => {
    if (!savedQuery) {
      setDialog({ open: true, mode: "create" });
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

  // Sharing is persisted on its own, without touching the SQL buffer: the content
  // baseline is deliberately left alone so unsaved edits stay unsaved.
  const setVisibility = useCallback(
    async (visibility: SavedQueryVisibility) => {
      if (!savedQuery || !canUpdateVisibility || saving) {
        return;
      }
      try {
        const res = await update({ id: savedQuery.id, visibility });
        if (res.ok) {
          setSavedQuery(res.savedQuery);
          toast.success(
            visibility === SavedQueryVisibility.Workspace
              ? t("Query shared with the workspace")
              : t("Query is now private"),
          );
        } else {
          toast.error(res.message);
        }
      } catch (err: any) {
        toast.error(err.message);
      }
    },
    [savedQuery, canUpdateVisibility, saving, update, t],
  );

  const saveAsNew = useCallback(
    () => setDialog({ open: true, mode: "create" }),
    [],
  );
  const editDetails = useCallback(
    () => setDialog({ open: true, mode: "edit-details" }),
    [],
  );
  const closeDialog = useCallback(
    () => setDialog((current) => ({ ...current, open: false })),
    [],
  );

  const onDialogSaved = useCallback(
    (sq: SavedQuery_SavedQueryFragment) => {
      if (dialog.mode === "edit-details") {
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
    saving,
    canUpdate,
    canUpdateVisibility,
    dialog,
    save,
    setVisibility,
    saveAsNew,
    editDetails,
    closeDialog,
    onDialogSaved,
  };
};
