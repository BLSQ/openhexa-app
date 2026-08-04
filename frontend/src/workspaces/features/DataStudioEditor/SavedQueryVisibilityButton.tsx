import { CheckIcon, ChevronDownIcon } from "@heroicons/react/20/solid";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Popover from "core/components/Popover";
import clsx from "clsx";
import { SavedQueryVisibility } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useState } from "react";
import { GHOST } from "workspaces/features/DataStudioEditor/toolbarStyles";
import {
  useSavedQueryVisibilityOption,
  useSavedQueryVisibilityOptions,
} from "workspaces/features/SavedQueries/savedQueryVisibility";
import SavedQueryVisibilityBadge from "workspaces/features/SavedQueries/SavedQueryVisibilityBadge";

type SavedQueryVisibilityButtonProps = {
  visibility: SavedQueryVisibility;
  canUpdate: boolean;
  saving: boolean;
  onChange: (visibility: SavedQueryVisibility) => void;
};

// Toolbar control for the current query's sharing, sitting next to Save because
// it is a decision about the query itself rather than about this session.
// Read-only for members who may edit the query but not unshare it.
const SavedQueryVisibilityButton = ({
  visibility,
  canUpdate,
  saving,
  onChange,
}: SavedQueryVisibilityButtonProps) => {
  const { t } = useTranslation();
  const options = useSavedQueryVisibilityOptions();
  const current = useSavedQueryVisibilityOption(visibility);
  // Set while a WORKSPACE -> PRIVATE switch waits for confirmation: unsharing takes
  // the query away from colleagues who can currently see it, so it is not a
  // one-click action like sharing is.
  const [pendingPrivate, setPendingPrivate] = useState(false);

  if (!canUpdate) {
    return (
      <SavedQueryVisibilityBadge
        visibility={visibility}
        className="px-2.5 text-xs font-medium text-gray-500"
      />
    );
  }

  const select = (next: SavedQueryVisibility) => {
    if (next === visibility) {
      return;
    }
    if (next === SavedQueryVisibility.Private) {
      setPendingPrivate(true);
      return;
    }
    onChange(next);
  };

  return (
    <>
      <Popover
        placement="bottom-end"
        buttonClassName={GHOST}
        className="w-72 p-1"
        trigger={
          <>
            <current.Icon
              className={clsx("h-4 w-4 shrink-0", current.iconClassName)}
            />
            {current.label}
            <ChevronDownIcon className="h-3.5 w-3.5 text-gray-400" />
          </>
        }
      >
        {({ close }) => (
          <div role="menu">
            {options.map(
              ({ value, label, description, Icon, iconClassName }) => (
                <button
                  key={value}
                  type="button"
                  role="menuitem"
                  disabled={saving}
                  onClick={() => {
                    close();
                    select(value);
                  }}
                  className={clsx(
                    "flex w-full items-start gap-2 rounded-md px-2.5 py-2 text-left",
                    value === visibility ? "bg-blue-50" : "hover:bg-gray-100",
                  )}
                >
                  <Icon
                    className={clsx("mt-0.5 h-4 w-4 shrink-0", iconClassName)}
                  />
                  <span className="min-w-0 flex-1">
                    <span className="flex items-center gap-1.5 text-xs font-medium text-gray-800">
                      {label}
                      {value === visibility && (
                        <CheckIcon className="h-3.5 w-3.5 text-blue-600" />
                      )}
                    </span>
                    <span className="mt-0.5 block text-xs text-gray-500">
                      {description}
                    </span>
                  </span>
                </button>
              ),
            )}
          </div>
        )}
      </Popover>

      <Dialog
        open={pendingPrivate}
        onClose={() => !saving && setPendingPrivate(false)}
        maxWidth="max-w-md"
      >
        <Dialog.Title onClose={() => setPendingPrivate(false)}>
          {t("Make this query private?")}
        </Dialog.Title>
        <Dialog.Content>
          <p className="text-sm text-gray-600">
            {t(
              "Other workspace members will no longer see or run this query. You can share it again at any time.",
            )}
          </p>
        </Dialog.Content>
        <Dialog.Actions>
          <Button
            variant="outlined"
            onClick={() => setPendingPrivate(false)}
            disabled={saving}
          >
            {t("Cancel")}
          </Button>
          <Button
            onClick={() => {
              setPendingPrivate(false);
              onChange(SavedQueryVisibility.Private);
            }}
            disabled={saving}
          >
            {t("Make private")}
          </Button>
        </Dialog.Actions>
      </Dialog>
    </>
  );
};

export default SavedQueryVisibilityButton;
