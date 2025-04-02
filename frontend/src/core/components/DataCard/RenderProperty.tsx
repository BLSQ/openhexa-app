import { ReactElement } from "react";
import { useDataCardProperty } from "./context";
import DataCard from "./DataCard";
import { DataCardSectionInstance, Property, PropertyDefinition } from "./types";

type RenderPropertyProps<T> = {
  children: (
    property: Property<T>,
    section: DataCardSectionInstance,
  ) => ReactElement;
} & PropertyDefinition;

function RenderProperty<T = any>(props: RenderPropertyProps<T>) {
  const { children, ...delegated } = props;
  const { property, section } = useDataCardProperty<T>(delegated);

  return (
    <DataCard.Property property={property}>
      {children(property, section)}
    </DataCard.Property>
  );
}

export default RenderProperty;
