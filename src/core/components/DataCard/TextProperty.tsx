import clsx from "clsx";
import ReactMarkdown from "react-markdown";
import Input from "../forms/Input";
import Textarea from "../forms/Textarea";
import { useDataCardProperty } from "./context";
import DataCard from "./DataCard";
import { PropertyDefinition } from "./types";

type TextPropertyProps = PropertyDefinition & {
  markdown?: boolean;
  defaultValue?: string;
  className?: string;
};

const TextProperty = (props: TextPropertyProps) => {
  const {
    markdown,
    defaultValue,
    id,
    accessor,
    required,
    readonly,
    label,
    help,
    className,
  } = props;

  const { property, section } = useDataCardProperty({
    id,
    accessor,
    required,
    readonly,
    label,
    help,
  });

  if (section.isEdited && !property.readonly) {
    return (
      <DataCard.Property property={property}>
        {markdown ? (
          <Textarea
            className="w-full"
            value={property.formValue}
            onChange={(e) => property.setValue(e.target.value)}
            required={property.required}
            readOnly={property.readonly}
          />
        ) : (
          <Input
            value={property.formValue ?? ""}
            onChange={(e) => property.setValue(e.target.value)}
            required={property.required}
            readOnly={property.readonly}
          />
        )}
      </DataCard.Property>
    );
  } else {
    return (
      <DataCard.Property property={property}>
        {markdown && property.displayValue ? (
          <ReactMarkdown className="prose max-w-3xl text-sm">
            {property.displayValue}
          </ReactMarkdown>
        ) : (
          <div className={clsx("prose text-sm text-gray-900", className)}>
            {property.displayValue || defaultValue}
          </div>
        )}
      </DataCard.Property>
    );
  }
};

export default TextProperty;
