import clsx from "clsx";
import { HTMLAttributes } from "react";

interface RadioOption {
  id: OptionId;
  label: string;
}

type OptionId = string;

interface RadioGroupProps extends HTMLAttributes<HTMLInputElement> {
  options: RadioOption[];
  value?: OptionId;
  disabled?: boolean;
  name: string;
}

const RadioGroup = ({
  name,
  options,
  disabled = false,
  onChange,
  value,
}: RadioGroupProps) => {
  return (
    <fieldset className="flex gap-4">
      {options.map((option) => (
        <div key={option.id} className="flex items-center">
          <input
            id={`${name}-${option.id}`}
            type="radio"
            name={name}
            disabled={disabled}
            className={clsx(
              "form-radio text-gray-800 focus:outline-hidden focus:ring-transparent",
            )}
            value={option.id}
            onChange={onChange}
            defaultChecked={option.id === value}
          />
          <label
            htmlFor={`${name}-${option.id}`}
            className="ml-2 text-sm font-medium text-gray-700"
          >
            {option.label}
          </label>
        </div>
      ))}
    </fieldset>
  );
};

export default RadioGroup;
