import { useTranslation } from "next-i18next";
import {
  GHOST,
  GHOST_DIRTY,
  GHOST_SECONDARY,
} from "workspaces/features/DataStudioEditor/toolbarStyles";
import { hasSavePath } from "./savePath";

// Heroicons has no floppy-disk/save glyph, so we inline the one from the Data
// Studio design (stroke style matches the Heroicons 24-outline set used around
// it in the toolbar).
const FloppyDiskIcon = ({ className }: { className?: string }) => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth={1.5}
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
    aria-hidden="true"
  >
    <path d="M5 4h11l3 3v13H5z" />
    <path d="M8 4v6h7V4" />
    <path d="M8 20v-6h8v6" />
  </svg>
);

// "Save as new" variant: the same floppy shrunk into the lower-left with a plus
// badge in the top-right corner, so the two save actions read as a family while
// signalling that this one forks a brand-new query.
const FloppyDiskPlusIcon = ({ className }: { className?: string }) => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth={1.5}
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
    aria-hidden="true"
  >
    <path d="M4 5h8l3 3v11H4z" />
    <path d="M7 5v4h5V5" />
    <path d="M7 19v-5h6v5" />
    <path d="M19 3.5v5" />
    <path d="M16.5 6h5" />
  </svg>
);

type SaveQueryButtonProps = {
  isSaved: boolean;
  isDirty: boolean;
  hasContent: boolean;
  canUpdate: boolean;
  canCreate: boolean;
  saving: boolean;
  onSave: () => void;
  onSaveAsNew: () => void;
};

// The Save control adapts to permissions and state:
// - new query           → single "Save" (opens the create dialog)
// - saved + can update   → primary "Save" + a muted "Save as new" sibling;
//   metadata edits happen via the pencil next to the query name
// - saved, cannot update → single "Save as new query" (the only way to persist)
const SaveQueryButton = ({
  isSaved,
  isDirty,
  hasContent,
  canUpdate,
  canCreate,
  saving,
  onSave,
  onSaveAsNew,
}: SaveQueryButtonProps) => {
  const { t } = useTranslation();

  // Shared with the navigation guard, which must not warn about changes that no
  // enabled control here could have saved.
  const canSave =
    hasSavePath({ isSaved, hasContent, canUpdate, canCreate }) && !saving;

  if (!isSaved) {
    if (!canCreate) {
      return null;
    }
    return (
      <button
        onClick={onSave}
        disabled={!canSave}
        className={GHOST}
        title={t("Save query")}
      >
        <FloppyDiskIcon className="h-4 w-4" />
        {t("Save")}
      </button>
    );
  }

  if (!canUpdate) {
    if (!canCreate) {
      return null;
    }
    return (
      <button
        onClick={onSaveAsNew}
        disabled={!canSave}
        className={GHOST}
        title={t("Save as a new query")}
      >
        <FloppyDiskPlusIcon className="h-4 w-4" />
        {t("Save as new query")}
      </button>
    );
  }

  const hasUnsavedEdits = isDirty && canSave;
  return (
    <div className="flex items-center gap-1">
      <button
        onClick={onSave}
        disabled={!hasUnsavedEdits}
        className={hasUnsavedEdits ? GHOST_DIRTY : GHOST}
        title={
          !hasContent
            ? t("The query is empty")
            : isDirty
              ? t("Save changes")
              : t("No changes to save")
        }
      >
        <FloppyDiskIcon className="h-4 w-4" />
        {t("Save")}
        {hasUnsavedEdits && (
          <span
            aria-hidden="true"
            className="h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500"
          />
        )}
      </button>
      <button
        onClick={onSaveAsNew}
        disabled={!canCreate || !canSave}
        className={GHOST_SECONDARY}
        title={t("Save as a new query")}
      >
        <FloppyDiskPlusIcon className="h-4 w-4" />
        {t("Save as new")}
      </button>
    </div>
  );
};

export default SaveQueryButton;
