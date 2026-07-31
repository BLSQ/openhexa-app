import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useCallback, useMemo, useState } from "react";
import { toast } from "react-toastify";
import { SavedQuery_SavedQueryFragment } from "workspaces/features/SavedQueries/SavedQueries.generated";
import { useSavedQueryMutations } from "workspaces/features/SavedQueries/useSavedQueryMutations";
import { dataStudioRoutes } from "workspaces/helpers/dataStudio";

type DialogState = { mode: "create" | "edit-details" } | null;

type UseSavedQueryEditorArgs = {
  workspaceSlug: string;
  content: string;
  initialSavedQuery?: SavedQuery_SavedQueryFragment | null;
  canCreate: boolean;
};

// What saving means for the buffer as it stands:
// - "create" → no saved query yet; persisting names it first (via the dialog)
// - "update" → a saved query the user may write to; persisting is in-place
// - "fork"   → a saved query the user may not write to; the only way to persist
//              their edits is a new query of their own
export type SaveVariant = "create" | "update" | "fork";

// The resolved save policy: which control the toolbar shows, and whether there
// is anything to persist right now. Single source of truth for both the Save
// button and the ⌘S shortcut, so the two can never disagree about what saving
// does — the shortcut runs exactly what the primary button would.
export type SavePlan = {
  // Null when the user can neither update the loaded query nor create one: no
  // save control is offered at all.
  variant: SaveVariant | null;
  // The primary save action, or null when there is nothing to persist.
  save: (() => void) | null;
  // Why `save` is unavailable, for the primary control's tooltip.
  blockedBy: "empty" | "clean" | "saving" | null;
  // The secondary "save as new" action, offered only alongside an updatable
  // query. Never what ⌘S runs.
  saveAsNew: (() => void) | null;
};

// Owns the write-path state machine for the SQL editor: whether the current
// buffer maps to a saved query, whether it has unsaved changes, and the
// save / save-as-new / edit-details actions plus the dialog they drive. Kept
// separate from run/export orchestration so each concern stays testable.
export const useSavedQueryEditor = ({
  workspaceSlug,
  content,
  initialSavedQuery,
  canCreate,
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

  const savePlan = useMemo<SavePlan>(() => {
    const variant: SaveVariant | null = !savedQuery
      ? canCreate
        ? "create"
        : null
      : canUpdate
        ? "update"
        : canCreate
          ? "fork"
          : null;

    if (!variant) {
      return { variant, save: null, blockedBy: null, saveAsNew: null };
    }

    // Only "update" has a baseline to diff against; create and fork persist to a
    // brand-new query, so any non-empty buffer is worth saving. "clean" outranks
    // "saving" because a query with nothing left to persist is better described
    // that way than as busy — which is also the state the frame right after an
    // in-place save lands in, while the mutation is still settling.
    const blockedBy = !hasContent
      ? "empty"
      : variant === "update" && !isDirty
        ? "clean"
        : saving
          ? "saving"
          : null;

    const primary = variant === "fork" ? saveAsNew : save;
    return {
      variant,
      save: blockedBy ? null : primary,
      blockedBy,
      saveAsNew:
        variant === "update" && canCreate && hasContent && !saving
          ? saveAsNew
          : null,
    };
  }, [
    savedQuery,
    canCreate,
    canUpdate,
    hasContent,
    isDirty,
    saving,
    save,
    saveAsNew,
  ]);

  // The "save now" command for callers with no button to click (the ⌘S/Ctrl+S
  // shortcut). Runs whatever the primary Save button would, or nothing at all.
  const commit = useCallback(() => {
    // An open modal owns the keyboard: ⌘S there belongs to its form, not to the
    // save that opened it. Unlike the states `savePlan` reports as blocked, this
    // one is about where focus sits rather than about what there is to persist.
    if (dialog) {
      return;
    }
    savePlan.save?.();
  }, [dialog, savePlan]);

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
    saving,
    canUpdate,
    dialog,
    savePlan,
    save,
    saveAsNew,
    commit,
    editDetails,
    closeDialog,
    onDialogSaved,
  };
};
