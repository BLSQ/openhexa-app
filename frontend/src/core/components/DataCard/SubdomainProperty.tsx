import clsx from "clsx";
import { useMemo } from "react";
import DataCard from "./DataCard";
import { useDataCardProperty } from "./context";
import { PropertyDefinition } from "./types";

type SubdomainPropertyProps = PropertyDefinition & {
  currentSubdomain?: string | null;
  serveUrl: string;
};

const SubdomainProperty = (props: SubdomainPropertyProps) => {
  const { currentSubdomain, serveUrl, ...delegated } = props;
  const { property, section } = useDataCardProperty(delegated);

  const urlParts = useMemo(() => {
    if (currentSubdomain && serveUrl) {
      try {
        const url = new URL(serveUrl);
        return {
          prefix: url.protocol + "//",
          suffix: url.host.substring(currentSubdomain.length),
        };
      } catch {
        return null;
      }
    }
    return null;
  }, [currentSubdomain, serveUrl]);

  if (!property.visible) {
    return null;
  }

  if (section.isEdited && !property.readonly) {
    return (
      <DataCard.Property property={property}>
        <div className="flex items-baseline gap-1 text-sm">
          {urlParts && <span className="text-gray-500">{urlParts.prefix}</span>}
          <input
            type="text"
            className={clsx(
              "form-input appearance-none",
              "px-2 py-1 border rounded-md focus:outline-hidden",
              "text-sm border-gray-300 text-gray-900",
              "focus:ring-blue-500 focus:border-blue-500",
              "w-40",
            )}
            value={property.formValue ?? ""}
            onChange={(e) => property.setValue(e.target.value)}
            required={property.required}
          />
          {urlParts && (
            <span className="text-gray-500">{urlParts.suffix}/</span>
          )}
        </div>
      </DataCard.Property>
    );
  } else {
    const fullUrl =
      urlParts && property.displayValue
        ? `${urlParts.prefix}${property.displayValue}${urlParts.suffix}`
        : null;

    return (
      <DataCard.Property property={property}>
        <div className="prose text-sm">
          {fullUrl ? (
            <a
              href={fullUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 underline hover:text-blue-400"
            >
              {fullUrl}
            </a>
          ) : (
            <span className="italic text-gray-500">-</span>
          )}
        </div>
      </DataCard.Property>
    );
  }
};

export default SubdomainProperty;
