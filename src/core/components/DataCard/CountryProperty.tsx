import CountryBadge from "core/features/CountryBadge";
import CountryPicker from "core/features/CountryPicker";
import { ensureArray } from "core/helpers/array";
import { useMemo } from "react";
import { useDataCardProperty } from "./context";
import DataCard from "./DataCard";
import { PropertyDefinition } from "./types";

type CountryPropertyProps = {
  multiple?: boolean;
} & PropertyDefinition;

const CountryProperty = (props: CountryPropertyProps) => {
  const { multiple, defaultValue, ...delegated } = props;
  const { property, section } = useDataCardProperty(delegated);

  const countriesArray = useMemo(
    () => ensureArray(property.displayValue),
    [property],
  );

  return (
    <DataCard.Property property={property}>
      {section.isEdited ? (
        <CountryPicker
          withPortal
          value={property.formValue ?? null}
          onChange={(v) => property.setValue(v)}
          multiple={multiple}
        />
      ) : (
        <div className="flex flex-wrap items-center gap-1.5">
          {countriesArray.length === 0 && defaultValue}
          {countriesArray.map((country, i) => (
            <CountryBadge key={i} country={country} />
          ))}
        </div>
      )}
    </DataCard.Property>
  );
};

export default CountryProperty;
