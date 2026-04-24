import Switch from "core/components/Switch";
import DataCard from "./DataCard";
import { useDataCardProperty } from "./context";
import { PropertyDefinition } from "./types";

type SwitchPropertyProps = PropertyDefinition & {
  onChange?: (checked: boolean) => void;
};

const SwitchProperty = (props: SwitchPropertyProps) => {
  const { onChange, ...rest } = props;
  const { property, section } = useDataCardProperty(rest);
  return (
    <DataCard.Property property={property}>
      <Switch
        disabled={!section.isEdited}
        checked={section.isEdited ? property.formValue : property.displayValue}
        onChange={(checked) => {
          property.setValue(checked);
          if (onChange) onChange(checked);
        }}
      />
    </DataCard.Property>
  );
};

export default SwitchProperty;
