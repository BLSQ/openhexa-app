import clsx from "clsx";
import SimpleSelect from "../forms/SimpleSelect";
import DataCard from "./DataCard";
import { useDataCardProperty } from "./context";
import { PropertyDefinition } from "./types";

type SimpleSelectPropertyProps<T = any> = Omit<
  PropertyDefinition,
  "defaultValue"
> & {
  options: T[];
  getOptionLabel?: (option: T) => string;
  getOptionValue?: (option: T) => string;
  defaultValue?: T;
  className?: string;
  onChange?: (value: T) => void;
};

const SimpleSelectProperty = <T,>(props: SimpleSelectPropertyProps<T>) => {
  const {
    options,
    getOptionLabel = (option: T) => String(option),
    getOptionValue = (option: T) => String(option),
    className,
    onChange,
    defaultValue,
    ...delegated
  } = props;

  const { property, section } = useDataCardProperty({
    ...delegated,
    defaultValue: defaultValue as any,
  });

  if (!property.visible) {
    return null;
  }

  if (section.isEdited && !property.readonly) {
    const currentValue = property.formValue;
    const selectedStringValue =
      currentValue != null ? getOptionValue(currentValue) : "";

    return (
      <DataCard.Property property={property}>
        <SimpleSelect
          value={selectedStringValue}
          onChange={(e) => {
            const selected = options.find(
              (opt) => getOptionValue(opt) === e.target.value,
            );
            if (selected !== undefined) {
              property.setValue(selected);
              onChange?.(selected);
            }
          }}
          required={property.required}
          disabled={property.readonly}
          className={className || "w-full"}
        >
          {options.map((option, i) => (
            <option key={i} value={getOptionValue(option)}>
              {getOptionLabel(option)}
            </option>
          ))}
        </SimpleSelect>
      </DataCard.Property>
    );
  } else {
    const displayValue = property.displayValue
      ? getOptionLabel(property.displayValue)
      : defaultValue
        ? getOptionLabel(defaultValue)
        : undefined;

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

export default SimpleSelectProperty;
