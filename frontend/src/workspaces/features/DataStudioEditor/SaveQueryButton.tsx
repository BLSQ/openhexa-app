import { Menu, MenuButton, MenuItem, MenuItems } from "@headlessui/react";
import { ChevronDownIcon } from "@heroicons/react/20/solid";
import clsx from "clsx";
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

type SaveQueryButtonProps = {
  isSaved: boolean;
  isDirty: boolean;
  hasContent: boolean;
  canUpdate: boolean;
  canCreate: boolean;
  saving: boolean;
  onSave: () => void;
  onSaveAsNew: () => void;
  onEditDetails: () => void;
};

const GHOST =
  "inline-flex h-8 items-center gap-1.5 rounded-md px-2.5 text-xs font-medium text-gray-700 hover:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-300 disabled:hover:bg-transparent";

const MENU_ITEM =
  "flex w-full items-center rounded-sm px-2 py-1.5 text-left text-xs text-gray-700 data-[focus]:bg-gray-100 data-[disabled]:cursor-not-allowed data-[disabled]:text-gray-300";

// The Save control adapts to permissions and state:
// - new query           → single "Save" (opens the create dialog)
// - saved + can update   → split "Save" + menu (save as new / edit details)
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
  onEditDetails,
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
        <FloppyDiskIcon className="h-4 w-4" />
        {t("Save as new query")}
      </button>
    );
  }

  return (
    <div className="flex items-center">
      <button
        onClick={onSave}
        disabled={!isDirty || saving}
        className={clsx(GHOST, "rounded-r-none pr-2")}
        title={isDirty ? t("Save changes") : t("No changes to save")}
      >
        <FloppyDiskIcon className="h-4 w-4" />
        {t("Save")}
      </button>
      <Menu as="div" className="relative">
        <MenuButton
          className={clsx(
            GHOST,
            "rounded-l-none border-l border-gray-200 px-1",
          )}
          aria-label={t("More save options")}
        >
          <ChevronDownIcon className="h-4 w-4" />
        </MenuButton>
        <MenuItems
          anchor="bottom end"
          className="z-30 mt-1 w-52 rounded-md bg-white p-1 shadow-lg ring-1 ring-black/5 focus:outline-none"
        >
          <MenuItem disabled={!canCreate}>
            <button onClick={onSaveAsNew} className={MENU_ITEM}>
              {t("Save as new query")}
            </button>
          </MenuItem>
          <MenuItem>
            <button onClick={onEditDetails} className={MENU_ITEM}>
              {t("Edit details…")}
            </button>
          </MenuItem>
        </MenuItems>
      </Menu>
    </div>
  );
};

export default SaveQueryButton;
