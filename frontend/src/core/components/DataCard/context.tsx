import * as React from "react";
import { DataCardSectionInstance, Property, PropertyDefinition } from "./types";

export const DataCardSectionContext =
  React.createContext<DataCardSectionInstance | null>(null);

export function useDataCardSection() {
  const section = React.useContext(DataCardSectionContext);
  if (!section) {
    throw new Error(
      "useDataCardSection must be wrapped by a DataCard.FormSection.",
    );
  }

  return section;
}

export function useDataCardProperty<V = any, FV = V>(
  definition: PropertyDefinition,
): { property: Property<V, FV>; section: DataCardSectionInstance } {
  const section = useDataCardSection();
  const property = section.setProperty(definition);

  return { property, section };
}
