import clsx from "clsx";
import DataCard from "./DataCard";
import { useDataCardProperty } from "./context";
import { PropertyDefinition } from "./types";

type LinkPropertyProps = Omit<PropertyDefinition, "readonly"> & {
  className?: string;
  defaultValue?: string;
};

const LinkProperty = (props: LinkPropertyProps) => {
  const { className, defaultValue, ...delegated } = props;

  const { property } = useDataCardProperty({
    ...delegated,
    readonly: true,
  });

  if (!property.visible) {
    return null;
  }

  return (
    <DataCard.Property property={property}>
      <div
        className={clsx(
          "prose text-sm",
          property.displayValue ? "text-gray-900" : "text-gray-500 italic",
          className,
        )}
      >
        {property.displayValue ? (
          <a
            href={property.displayValue}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-500 underline hover:text-blue-400"
          >
            {property.displayValue}
          </a>
        ) : (
          defaultValue
        )}
      </div>
    </DataCard.Property>
  );
};

export default LinkProperty;
