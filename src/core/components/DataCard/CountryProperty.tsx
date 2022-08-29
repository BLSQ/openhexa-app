import CountryBadge from "core/features/CountryBadge";
import CountryPicker from "core/features/CountryPicker";
import { ensureArray } from "core/helpers/array";
import { useDataCardProperty } from "./context";
import DataCard from "./DataCard";
import { PropertyDefinition } from "./types";

type CountryPropertyProps = { multiple?: boolean } & PropertyDefinition;

const CountryProperty = (props: CountryPropertyProps) => {
  const { multiple, ...delegated } = props;
  const { property, section } = useDataCardProperty(delegated);

  return (
    <DataCard.Property property={property}>
      {section.isEdited ? (
        <CountryPicker
          value={property.formValue}
          onChange={(v) => property.setValue(v)}
          multiple={multiple}
        />
      ) : (
        <div className="flex flex-wrap items-center gap-1.5">
          {ensureArray(property.displayValue).map((country, i) => (
            <CountryBadge key={i} country={country} />
          ))}
        </div>
      )}
    </DataCard.Property>
  );
};

export default CountryProperty;
