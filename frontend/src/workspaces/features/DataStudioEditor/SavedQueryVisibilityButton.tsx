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
  // Sharing with the workspace and unsharing (the author's right).
  canUpdate: boolean;
  // Making the query public (an organization admin's right).
  canPublish: boolean;
  saving: boolean;
  onChange: (visibility: SavedQueryVisibility) => void;
};

// Toolbar control for the current query's sharing, sitting next to Save because
// it is a decision about the query itself rather than about this session.
// Read-only for members who may edit the query but neither unshare nor publish it.
const SavedQueryVisibilityButton = ({
  visibility,
  canUpdate,
  canPublish,
  saving,
  onChange,
}: SavedQueryVisibilityButtonProps) => {
  const { t } = useTranslation();
  const options = useSavedQueryVisibilityOptions();
  const current = useSavedQueryVisibilityOption(visibility);
  // Set while a switch that takes the query away from someone waits for
  // confirmation: unsharing takes it from colleagues, publishing hands it to
  // the whole internet, unpublishing breaks a link that may be in use. None of
  // those is a one-click action like sharing with the workspace is.
  const [pending, setPending] = useState<SavedQueryVisibility | null>(null);

  if (!canUpdate && !canPublish) {
    return <SavedQueryVisibilityBadge visibility={visibility} />;
  }

  const isOptionDisabled = (next: SavedQueryVisibility) =>
    saving ||
    (next !== visibility &&
      (next === SavedQueryVisibility.Public ? !canPublish : !canUpdate));

  const select = (next: SavedQueryVisibility) => {
    if (next === visibility) {
      return;
    }
    const needsConfirmation =
      next === SavedQueryVisibility.Private ||
      next === SavedQueryVisibility.Public ||
      visibility === SavedQueryVisibility.Public;
    if (needsConfirmation) {
      setPending(next);
      return;
    }
    onChange(next);
  };

  const confirmation = {
    [SavedQueryVisibility.Private]: {
      title: t("Make this query private?"),
      body: t(
        "Other workspace members will no longer see or run this query. You can share it again at any time.",
      ),
      action: t("Make private"),
    },
    [SavedQueryVisibility.Workspace]: {
      title: t("Stop sharing this query publicly?"),
      body: t(
        "The public link will stop working. Workspace members keep access to the query.",
      ),
      action: t("Stop sharing publicly"),
    },
    [SavedQueryVisibility.Public]: {
      title: t("Make this query public?"),
      body: t(
        "Anyone with the link will be able to run this query and export its result, without an OpenHEXA account. You can take it back at any time.",
      ),
      action: t("Make public"),
    },
  }[pending ?? SavedQueryVisibility.Private];

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
                  disabled={isOptionDisabled(value)}
                  onClick={() => {
                    close();
                    select(value);
                  }}
                  className={clsx(
                    "flex w-full items-start gap-2 rounded-md px-2.5 py-2 text-left disabled:cursor-not-allowed disabled:opacity-50",
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
            {!canPublish && visibility !== SavedQueryVisibility.Public && (
              <p className="px-2.5 py-2 text-xs text-gray-400">
                {t(
                  "Only organization admins and owners can make a query public.",
                )}
              </p>
            )}
          </div>
        )}
      </Popover>

      <Dialog
        open={pending !== null}
        onClose={() => !saving && setPending(null)}
        maxWidth="max-w-md"
      >
        <Dialog.Title onClose={() => setPending(null)}>
          {confirmation.title}
        </Dialog.Title>
        <Dialog.Content>
          <p className="text-sm text-gray-600">{confirmation.body}</p>
        </Dialog.Content>
        <Dialog.Actions>
          <Button
            variant="outlined"
            onClick={() => setPending(null)}
            disabled={saving}
          >
            {t("Cancel")}
          </Button>
          <Button
            onClick={() => {
              const next = pending;
              setPending(null);
              if (next) {
                onChange(next);
              }
            }}
            disabled={saving}
          >
            {confirmation.action}
          </Button>
        </Dialog.Actions>
      </Dialog>
    </>
  );
};

export default SavedQueryVisibilityButton;
