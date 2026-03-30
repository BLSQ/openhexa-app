import clsx from "clsx";
import { useMemo } from "react";
import Input from "../forms/Input";
import DataCard from "./DataCard";
import { useDataCardProperty } from "./context";
import { PropertyDefinition } from "./types";

type SubdomainPropertyProps = PropertyDefinition & {
  currentSubdomain?: string | null;
  subdomainUrl?: string | null;
};

const SubdomainProperty = (props: SubdomainPropertyProps) => {
  const { currentSubdomain, subdomainUrl, ...delegated } = props;
  const { property, section } = useDataCardProperty(delegated);

  const urlParts = useMemo(() => {
    if (currentSubdomain && subdomainUrl) {
      try {
        const url = new URL(subdomainUrl);
        return {
          prefix: url.protocol + "//",
          suffix: url.host.substring(currentSubdomain.length),
        };
      } catch {
        return null;
      }
    }
    return null;
  }, [currentSubdomain, subdomainUrl]);

  if (!property.visible) {
    return null;
  }

  if (section.isEdited && !property.readonly) {
    const previewUrl =
      urlParts && property.formValue
        ? `${urlParts.prefix}${property.formValue}${urlParts.suffix}`
        : null;

    return (
      <DataCard.Property property={property}>
        <Input
          fullWidth
          value={property.formValue ?? ""}
          onChange={(e) => property.setValue(e.target.value)}
          required={property.required}
          readOnly={property.readonly}
        />
        {previewUrl && (
          <p className="mt-1 text-xs text-gray-500">{previewUrl}</p>
        )}
      </DataCard.Property>
    );
  } else {
    return (
      <DataCard.Property property={property}>
        <div
          className={clsx(
            "prose text-sm",
            property.displayValue ? "text-gray-900" : "text-gray-500 italic",
          )}
        >
          {property.displayValue || "-"}
        </div>
      </DataCard.Property>
    );
  }
};

export default SubdomainProperty;
