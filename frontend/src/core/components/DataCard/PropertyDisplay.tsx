import { ReactNode } from "react";
import DescriptionList from "../DescriptionList";
import { useDataCardSection } from "./context";
import { Property } from "./types";

export interface PropertyDisplayProps {
  property: Property;
  children: ReactNode;
}

const PropertyDisplay = (props: PropertyDisplayProps) => {
  const { property, children } = props;
  const section = useDataCardSection();

  const error =
    section.isEdited &&
    section.form.touched[property.id] &&
    section.form.errors[property.id];

  if (property.hideLabel && !section.isEdited) {
    return <>{children}</>;
  } else if (property.visible) {
    return (
      <DescriptionList.Item label={property.label} help={property.help}>
        {children}
        {error && <div className="mt-1 text-xs text-red-500">{error}</div>}
      </DescriptionList.Item>
    );
  } else {
    return null;
  }
};

export default PropertyDisplay;
