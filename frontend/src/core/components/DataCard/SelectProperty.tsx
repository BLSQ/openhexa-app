import clsx from "clsx";
import Select from "../forms/Select";
import DataCard from "./DataCard";
import { useDataCardProperty } from "./context";
import { PropertyDefinition } from "./types";

type SelectPropertyProps<T = any> = PropertyDefinition & {
  options: T[];
  getOptionLabel?: (option: T) => string;
  defaultValue?: string;
  nullable?: boolean;
  className?: string;
  onChange?: (value: T) => void;
};

const SelectProperty = <T,>(props: SelectPropertyProps<T>) => {
  const {
    options,
    getOptionLabel = (option: T) => String(option),
    defaultValue,
    nullable = false,
    className,
    onChange,
    ...delegated
  } = props;

  const { property, section } = useDataCardProperty(delegated);

  if (!property.visible) {
    return null;
  }

  if (section.isEdited && !property.readonly) {
    return (
      <DataCard.Property property={property}>
        <Select
          options={nullable ? [null, ...options] : options}
          value={property.formValue ?? null}
          onChange={(value) => {
            property.setValue(value);
            onChange?.(value);
          }}
          getOptionLabel={(option) => {
            if (option === null) return defaultValue || "Not set";
            return getOptionLabel(option);
          }}
          displayValue={(option) => {
            if (option === null) return "";
            return getOptionLabel(option);
          }}
          required={property.required}
          disabled={property.readonly}
          className={className || "w-full"}
        />
      </DataCard.Property>
    );
  } else {
    const displayValue = property.displayValue
      ? getOptionLabel(property.displayValue)
      : defaultValue;

    return (
      <DataCard.Property property={property}>
        <div
          className={clsx(
            "prose text-sm",
            property.displayValue ? "text-gray-900" : "text-gray-500 italic",
            className,
          )}
        >
          {displayValue}
        </div>
      </DataCard.Property>
    );
  }
};

export default SelectProperty;
