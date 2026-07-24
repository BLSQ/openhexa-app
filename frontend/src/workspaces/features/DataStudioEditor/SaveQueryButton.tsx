import { useTranslation } from "next-i18next";

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

const GHOST =
  "inline-flex h-8 items-center gap-1.5 rounded-md px-2.5 text-xs font-medium text-gray-700 hover:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-300 disabled:hover:bg-transparent";

// Muted sibling of GHOST for the secondary "Save as new" action, so it reads as
// clearly subordinate to the primary Save without hiding it in a menu.
const GHOST_SECONDARY =
  "inline-flex h-8 items-center gap-1.5 rounded-md px-2.5 text-xs font-medium text-gray-500 hover:bg-gray-100 hover:text-gray-700 disabled:cursor-not-allowed disabled:text-gray-300 disabled:hover:bg-transparent";

// Amber accent for the primary Save when a saved query has unsaved edits, so the
// button itself signals "you have work to persist" (no separate dirty dot). Only
// applied while the button is actionable, so it never tints the disabled state.
const GHOST_DIRTY =
  "inline-flex h-8 items-center gap-1.5 rounded-md px-2.5 text-xs font-medium text-amber-600 hover:bg-amber-50 hover:text-amber-700";

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

  if (!isSaved) {
    if (!canCreate) {
      return null;
    }
    return (
      <button
        onClick={onSave}
        disabled={!hasContent || saving}
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
        disabled={!hasContent || saving}
        className={GHOST}
        title={t("Save as a new query")}
      >
        <FloppyDiskPlusIcon className="h-4 w-4" />
        {t("Save as new query")}
      </button>
    );
  }

  const hasUnsavedEdits = isDirty && hasContent && !saving;
  return (
    <div className="flex items-center gap-1">
      <button
        onClick={onSave}
        disabled={!isDirty || !hasContent || saving}
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
        disabled={!canCreate || !hasContent || saving}
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
