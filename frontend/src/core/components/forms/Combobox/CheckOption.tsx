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
      className={({ focus }) =>
        clsx(
          "relative cursor-default select-none px-2 py-2",
          focus ? "bg-blue-500 text-white" : "text-gray-900",
          className,
        )
      }
    >
      {({ focus, selected }) => (
        <div className="group flex w-full items-center">
          <span
            className={clsx(
              "flex items-center pr-4",
              !selected && !forceSelected && "invisible",
              focus ? "text-white" : "text-gray-900",
            )}
          >
            <CheckIcon
              className={clsx(
                "h-5 w-5",
                (selected || forceSelected) && !focus && "text-blue-500",
              )}
              aria-hidden="true"
            />
          </span>
          <span
            className={clsx(
              "flex-1 truncate",
              (selected || forceSelected) && "font-semibold",
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
