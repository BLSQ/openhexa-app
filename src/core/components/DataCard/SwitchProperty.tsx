import Switch from "core/components/Switch";
import DataCard from "./DataCard";
import { useDataCardProperty } from "./context";
import { PropertyDefinition } from "./types";

type SwitchPropertyProps = PropertyDefinition;

const SwitchProperty = (props: SwitchPropertyProps) => {
  const { property, section } = useDataCardProperty(props);
  return (
    <DataCard.Property property={property}>
      <Switch
        disabled={!section.isEdited}
        checked={section.isEdited ? property.formValue : property.displayValue}
        onChange={(checked) => property.setValue(checked)}
      />
    </DataCard.Property>
  );
};

export default SwitchProperty;
