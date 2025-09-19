import DataCard from "core/components/DataCard/DataCard";
import { useDataCardProperty } from "core/components/DataCard/context";
import { PropertyDefinition } from "core/components/DataCard/types";
import ConfigurationList from "../ConfigurationList";

type ConfigurationPropertyProps = PropertyDefinition & {
  defaultValue?: Record<string, any>;
};

const ConfigurationProperty = (props: ConfigurationPropertyProps) => {
  const { defaultValue = {}, ...delegated } = props;

  const { property, section } = useDataCardProperty(delegated);

  if (!property.visible) {
    return null;
  }

  if (section.isEdited && !property.readonly) {
    const currentValue = property.formValue || defaultValue;
    return (
      <DataCard.Property property={property}>
        <ConfigurationList
          configuration={currentValue}
          onChange={(newConfig) => property.setValue(newConfig)}
          disabled={property.readonly}
        />
      </DataCard.Property>
    );
  }

  const currentValue = property.displayValue || defaultValue;
  const hasConfiguration = currentValue && Object.keys(currentValue).length > 0;

  return (
    <DataCard.Property property={property}>
      {hasConfiguration ? (
        <ConfigurationList
          configuration={currentValue}
          onChange={() => {}}
          disabled={true}
        />
      ) : (
        <div className="prose text-sm text-gray-500 italic">Not set</div>
      )}
    </DataCard.Property>
  );
};

export default ConfigurationProperty;
