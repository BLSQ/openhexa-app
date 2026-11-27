import clsx from "clsx";
import { SharingOption } from "core/features/Sharing/sharingStyles";
import { ReactNode } from "react";

type SharingPickerProps<V extends string> = {
  options: SharingOption<V>[];
  value: V;
  onChange: (value: V) => void;
  isOptionDisabled?: (value: V) => boolean;
  hint?: ReactNode;
};

// Card-style radio group: each option carries a one-line explanation, because
// who gets access is a consequence users should not have to infer. Built on
// real radio inputs so keyboard and screen-reader behaviour comes for free.
const SharingPicker = <V extends string>({
  options,
  value,
  onChange,
  isOptionDisabled = () => false,
  hint,
}: SharingPickerProps<V>) => (
  // Side by side when there is room (a page), stacked in a dialog.
  <div className="@container">
    <div className="grid grid-cols-1 gap-2 @2xl:grid-cols-3">
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
    {hint && <p className="mt-2 text-xs text-gray-500">{hint}</p>}
  </div>
);

export default SharingPicker;
