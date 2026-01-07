import { CheckIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import { ComboboxOption as UIComboboxOption } from "@headlessui/react";
import { ReactNode } from "react";

type CheckOptionsProps = {
  value: any;
  className?: string;
  disabled?: boolean;
  forceSelected?: boolean;
  children?:
    | ReactNode
    | (({
        active,
        selected,
      }: {
        active: boolean;
        selected: boolean;
      }) => ReactNode);
};

function CheckOption(props: CheckOptionsProps) {
  const {
    value,
    className,
    children,
    disabled = false,
    forceSelected = false,
  } = props;

  return (
    <UIComboboxOption
      value={value}
      disabled={disabled}
      className={({ focus, selected }) =>
        clsx(
          "relative cursor-default select-none px-3 py-2 rounded-md mx-1",
          focus && "bg-gray-100",
          selected || forceSelected ? "bg-gray-50" : "",
          className,
        )
      }
    >
      {({ focus, selected }) => (
        <div className="group flex w-full items-center gap-3">
          <span
            className={clsx(
              "flex h-4 w-4 items-center justify-center rounded border transition-colors",
              selected || forceSelected
                ? "bg-blue-500 border-blue-500"
                : "border-gray-300",
            )}
          >
            {(selected || forceSelected) && (
              <CheckIcon className="h-3 w-3 text-white" aria-hidden="true" />
            )}
          </span>
          <span
            className={clsx(
              "flex-1 truncate text-gray-700",
              (selected || forceSelected) && "text-gray-900",
            )}
          >
            {typeof children === "function"
              ? children({ active: focus, selected: selected || forceSelected })
              : children}
          </span>
        </div>
      )}
    </UIComboboxOption>
  );
}

export default CheckOption;
