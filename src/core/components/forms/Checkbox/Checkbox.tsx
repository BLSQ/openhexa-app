import { InformationCircleIcon } from "@heroicons/react/24/solid";
import clsx from "clsx";
import Tooltip from "core/components/Tooltip/Tooltip";
import { InputHTMLAttributes, ReactNode } from "react";

interface CheckboxProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: ReactNode;
  description?: string;
  help?: string;
}

const Checkbox = (props: CheckboxProps) => {
  const { id, name, label, description, className, help, ...delegated } = props;

  const inputClassName = clsx(
    "form-checkbox h-4 w-4 text-blue-500 border-gray-300 rounded-sm focus:ring-0 focus:ring-offset-0",
  );
  return (
    <div className={clsx("relative flex items-start", className)}>
      <div className="flex h-5 items-center">
        <input
          id={id ?? name}
          name={name}
          type="checkbox"
          className={inputClassName}
          {...delegated}
        />
      </div>
      {(label || description) && (
        <div className="ml-2 text-sm">
          {label && (
            <label htmlFor={name} className="text-gray-900">
              {label}
            </label>
          )}
          {description && (
            <p id={`${name}-description`} className="text-gray-400">
              {description}
            </p>
          )}
        </div>
      )}
      {help && (
        <Tooltip label={help}>
          <InformationCircleIcon className="ml-1 h-3 w-3" />
        </Tooltip>
      )}
    </div>
  );
};

export default Checkbox;
