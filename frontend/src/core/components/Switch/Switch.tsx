import { Field, Label, Switch as HeadlessSwitch } from "@headlessui/react";
import clsx from "clsx";

export type SwitchProps = {
  onChange?(checked: boolean): void;
  checked: boolean;
  name?: string;
  disabled?: boolean;
  labelClassName?: string;
  label?: string;
  passive?: boolean;
};

const Switch = (props: SwitchProps) => {
  const {
    label,
    name,
    disabled = false,
    passive = false,
    checked,
    onChange = () => {},
    labelClassName,
    ...delegated
  } = props;
  return (
    <Field>
      <div className="flex items-center">
        {label && (
          <Label
            title={label}
            className={clsx("mr-4  text-gray-600", labelClassName)}
            passive={passive}
          >
            {label}
          </Label>
        )}
        <HeadlessSwitch
          onChange={onChange}
          disabled={disabled}
          name={name}
          checked={checked}
          {...delegated}
          className={clsx(
            "relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors focus:outline-hidden focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2",
            disabled && "cursor-not-allowed bg-opacity-70",
            disabled && (checked ? "bg-blue-600" : "bg-gray-200"),
            !disabled && (checked ? "bg-blue-600/70" : "bg-gray-200/70"),
          )}
        >
          <span
            className={`${
              checked ? "translate-x-6" : "translate-x-1"
            } inline-block h-4 w-4 transform rounded-full bg-white transition-transform`}
          />
        </HeadlessSwitch>
      </div>
    </Field>
  );
};

export default Switch;
