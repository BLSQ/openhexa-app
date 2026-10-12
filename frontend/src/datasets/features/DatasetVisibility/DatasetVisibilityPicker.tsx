import clsx from "clsx";
import { DatasetVisibility } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useDatasetVisibilityOptions } from "./datasetVisibility";

type DatasetVisibilityPickerProps = {
  value: DatasetVisibility;
  onChange: (visibility: DatasetVisibility) => void;
  disabled?: boolean;
  canMakePublic: boolean;
};

// Card-style radio group: each option spells out who gets access, because the
// difference between "organization" and "public" is a consequence users should
// not have to infer from a label.
const DatasetVisibilityPicker = ({
  value,
  onChange,
  disabled = false,
  canMakePublic,
}: DatasetVisibilityPickerProps) => {
  const { t } = useTranslation();
  const options = useDatasetVisibilityOptions();

  // Publishing is reserved to organization admins, but an already public
  // dataset must still show its current state as selected.
  const isOptionDisabled = (optionValue: DatasetVisibility) =>
    disabled ||
    (optionValue === DatasetVisibility.Public &&
      !canMakePublic &&
      value !== DatasetVisibility.Public);

  return (
    <div>
      <div
        className="grid grid-cols-1 gap-2 sm:grid-cols-3"
        role="radiogroup"
        aria-label={t("Visibility")}
      >
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
                  name="dataset-visibility"
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
      {!disabled && !canMakePublic && (
        <p className="mt-2 text-xs text-gray-500">
          {t("Only organization admins and owners can make a dataset public.")}
        </p>
      )}
    </div>
  );
};

export default DatasetVisibilityPicker;
