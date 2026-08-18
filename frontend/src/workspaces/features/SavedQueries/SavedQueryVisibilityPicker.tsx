import clsx from "clsx";
import { SavedQueryVisibility } from "graphql/types";
import { useSavedQueryVisibilityOptions } from "workspaces/features/SavedQueries/savedQueryVisibility";

type SavedQueryVisibilityPickerProps = {
  value: SavedQueryVisibility;
  onChange: (visibility: SavedQueryVisibility) => void;
  disabled?: boolean;
};

// Card-style radio group: each option carries a one-line explanation, because
// "Private" vs "Workspace" is a consequence users should not have to infer.
// Built on real radio inputs so keyboard and screen-reader behaviour comes for free.
const SavedQueryVisibilityPicker = ({
  value,
  onChange,
  disabled = false,
}: SavedQueryVisibilityPickerProps) => {
  const options = useSavedQueryVisibilityOptions();

  return (
    <div className="grid grid-cols-2 gap-2">
      {options.map(
        ({ value: optionValue, label, description, Icon, iconClassName }) => {
          const selected = optionValue === value;
          return (
            <label
              key={optionValue}
              className={clsx(
                "rounded-md border p-2.5 transition-colors",
                selected
                  ? "border-blue-500 bg-blue-50/50 ring-1 ring-blue-500/30"
                  : "border-gray-200",
                disabled
                  ? "cursor-not-allowed opacity-60"
                  : "cursor-pointer hover:bg-gray-50",
              )}
            >
              <input
                type="radio"
                name="visibility"
                value={optionValue}
                checked={selected}
                disabled={disabled}
                onChange={() => onChange(optionValue)}
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
  );
};

export default SavedQueryVisibilityPicker;
