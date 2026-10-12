import clsx from "clsx";
import { SavedQueryVisibility } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useSavedQueryVisibilityOptions } from "workspaces/features/SavedQueries/savedQueryVisibility";

type SavedQueryVisibilityPickerProps = {
  value: SavedQueryVisibility;
  onChange: (visibility: SavedQueryVisibility) => void;
  disabled?: boolean;
  // Sharing with the workspace (and unsharing) is the author's right; publishing
  // is an organization admin's. The two are gated separately because a user can
  // hold either one without the other.
  canShare?: boolean;
  canPublish?: boolean;
};

// Card-style radio group: each option carries a one-line explanation, because
// "Private" vs "Workspace" vs "Public" is a consequence users should not have to
// infer. Built on real radio inputs so keyboard and screen-reader behaviour
// comes for free.
const SavedQueryVisibilityPicker = ({
  value,
  onChange,
  disabled = false,
  canShare = true,
  canPublish = false,
}: SavedQueryVisibilityPickerProps) => {
  const { t } = useTranslation();
  const options = useSavedQueryVisibilityOptions();

  // The current value always stays selectable (a no-op), so a query whose
  // visibility the user may not change still shows its state as checked.
  const isOptionDisabled = (optionValue: SavedQueryVisibility) => {
    if (disabled) {
      return true;
    }
    if (optionValue === value) {
      return false;
    }
    return optionValue === SavedQueryVisibility.Public
      ? !canPublish
      : !canShare;
  };

  return (
    <div>
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
        {options.map(
          ({ value: optionValue, label, description, Icon, iconClassName }) => {
            const selected = optionValue === value;
            const optionDisabled = isOptionDisabled(optionValue);
            return (
              <label
                key={optionValue}
                className={clsx(
                  "rounded-md border p-2.5 transition-colors",
                  selected
                    ? "border-blue-500 bg-blue-50/50 ring-1 ring-blue-500/30"
                    : "border-gray-200",
                  optionDisabled
                    ? "cursor-not-allowed opacity-60"
                    : "cursor-pointer hover:bg-gray-50",
                )}
              >
                <input
                  type="radio"
                  name="visibility"
                  value={optionValue}
                  checked={selected}
                  disabled={optionDisabled}
                  onChange={() => !optionDisabled && onChange(optionValue)}
                  className="sr-only"
                />
                <span className="flex items-center gap-1.5 text-sm font-medium text-gray-800">
                  <Icon className={clsx("h-4 w-4 shrink-0", iconClassName)} />
                  {label}
                </span>
                <span className="mt-0.5 block text-xs text-gray-500">
                  {description}
                </span>
              </label>
            );
          },
        )}
      </div>
      {!disabled && !canPublish && value !== SavedQueryVisibility.Public && (
        <p className="mt-2 text-xs text-gray-500">
          {t("Only organization admins and owners can make a query public.")}
        </p>
      )}
    </div>
  );
};

export default SavedQueryVisibilityPicker;
