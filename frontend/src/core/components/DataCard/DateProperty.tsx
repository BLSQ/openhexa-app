import { DateTimeFormatOptions } from "luxon";
import { useMemo } from "react";
import Input from "../forms/Input";
import Time from "../Time";
import { useDataCardProperty } from "./context";
import DataCard from "./DataCard";
import { PropertyDefinition } from "./types";

type DatePropertyProps = PropertyDefinition & {
  format?: DateTimeFormatOptions;
  relative?: boolean;
  min?: string;
  max?: string;
  markdown?: boolean;
};

const DateProperty = (props: DatePropertyProps) => {
  const { format, min, max, relative, ...delegated } = props;

  const { property, section } = useDataCardProperty(delegated);

  const value = useMemo(() => {
    return property.formValue?.split(".")[0];
  }, [property.formValue]);

  return (
    <DataCard.Property property={property}>
      {section.isEdited && !property.readonly ? (
        <Input
          name={property.id}
          type="datetime-local"
          required={property.required}
          value={value}
          min={min}
          max={max}
          onChange={(e) => property.setValue(e.target.value)}
        />
      ) : (
        property.displayValue && (
          <Time
            relative={relative}
            datetime={property.displayValue}
            format={format}
          />
        )
      )}
    </DataCard.Property>
  );
};

export default DateProperty;
