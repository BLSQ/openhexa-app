import { useTranslation } from "next-i18next";
import useIsMac from "core/hooks/useIsMac";
import { SavePlan } from "./useSavedQueryEditor";

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
  /** The resolved save policy from `useSavedQueryEditor`. */
  plan: SavePlan;
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

// Renders `plan.variant`; the plan (not this component) decides what saving
// means and whether it is available, so the toolbar and ⌘S can never diverge.
// - "create" → single "Save" (opens the create dialog)
// - "update" → primary "Save" + a muted "Save as new" sibling; metadata edits
//   happen via the pencil next to the query name
// - "fork"   → single "Save as new query" (the only way to persist)
// The shortcut hint annotates only the control ⌘S actually triggers, so the
// muted "Save as new" sibling stays hint-free while the fork variant carries it.
const SaveQueryButton = ({ plan }: SaveQueryButtonProps) => {
  const { t } = useTranslation();
  const isMac = useIsMac();

  // Appended here rather than interpolated into the translated strings: the
  // shortcut is not language, and this way the tooltips keep reusing their
  // existing labels instead of needing a shortcut-bearing variant of each.
  const withShortcut = (label: string) =>
    `${label} (${isMac ? "⌘S" : "Ctrl+S"})`;

  if (!plan.variant) {
    return null;
  }

  if (plan.variant === "create") {
    return (
      <button
        onClick={plan.save ?? undefined}
        disabled={!plan.save}
        className={GHOST}
        title={withShortcut(t("Save query"))}
      >
        <FloppyDiskIcon className="h-4 w-4" />
        {t("Save")}
      </button>
    );
  }

  if (plan.variant === "fork") {
    return (
      <button
        onClick={plan.save ?? undefined}
        disabled={!plan.save}
        className={GHOST}
        title={withShortcut(t("Save as a new query"))}
      >
        <FloppyDiskPlusIcon className="h-4 w-4" />
        {t("Save as new query")}
      </button>
    );
  }

  // In the "update" variant an available save means exactly "there are edits to
  // persist", which is what the amber accent signals.
  const hasUnsavedEdits = Boolean(plan.save);
  return (
    <div className="flex items-center gap-1">
      <button
        onClick={plan.save ?? undefined}
        disabled={!plan.save}
        className={hasUnsavedEdits ? GHOST_DIRTY : GHOST}
        title={
          plan.blockedBy === "empty"
            ? t("The query is empty")
            : plan.blockedBy === "clean"
              ? t("No changes to save")
              : withShortcut(t("Save changes"))
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
        onClick={plan.saveAsNew ?? undefined}
        disabled={!plan.saveAsNew}
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
