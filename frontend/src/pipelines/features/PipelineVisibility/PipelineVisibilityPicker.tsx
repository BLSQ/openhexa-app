import clsx from "clsx";
import { PipelineVisibility } from "graphql/types";
import { useTranslation } from "next-i18next";
import { usePipelineVisibilityOptions } from "./pipelineVisibility";

type PipelineVisibilityPickerProps = {
  value: PipelineVisibility;
  onChange: (visibility: PipelineVisibility) => void;
  disabled?: boolean;
  // Publishing is an organization admin's call; taking a pipeline back is
  // anyone's who can edit it.
  canPublish?: boolean;
};

// Card-style radio group, the same shape as the dataset and saved query
// pickers: each option carries a one-line explanation, because what "Public"
// opens is a consequence users should not have to infer.
const PipelineVisibilityPicker = ({
  value,
  onChange,
  disabled = false,
  canPublish = false,
}: PipelineVisibilityPickerProps) => {
  const { t } = useTranslation();
  const options = usePipelineVisibilityOptions();

  // The current value always stays selectable (a no-op), so a pipeline whose
  // visibility the user may not change still shows its state as checked.
  const isOptionDisabled = (optionValue: PipelineVisibility) =>
    disabled ||
    (optionValue !== value &&
      optionValue === PipelineVisibility.Public &&
      !canPublish);

  return (
    <div>
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
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
      {!disabled && !canPublish && value !== PipelineVisibility.Public && (
        <p className="mt-2 text-xs text-gray-500">
          {t("Only organization admins and owners can make a pipeline public.")}
        </p>
      )}
    </div>
  );
};

export default PipelineVisibilityPicker;
