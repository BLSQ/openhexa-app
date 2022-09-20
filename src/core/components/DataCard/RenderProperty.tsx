import { ReactElement } from "react";
import { useDataCardProperty } from "./context";
import DataCard from "./DataCard";
import { PropertyDefinition } from "./types";

type RenderPropertyProps<T> = {
  children: (item: T) => ReactElement;
} & PropertyDefinition;

function RenderProperty<T = any>(props: RenderPropertyProps<T>) {
  const { children, ...delegated } = props;
  const { property } = useDataCardProperty<T>(delegated);

  return (
    <DataCard.Property property={property}>
      {children(property.displayValue)}
    </DataCard.Property>
  );
}

export default RenderProperty;
