import clsx from "clsx";
import MarkdownViewer from "../MarkdownViewer";
import Input from "../forms/Input";
import Textarea from "../forms/Textarea";
import DataCard from "./DataCard";
import { useDataCardProperty } from "./context";
import { PropertyDefinition } from "./types";
import { TextareaProps } from "../forms/Textarea/Textarea";

type TextPropertyProps = PropertyDefinition & {
  markdown?: boolean;
  defaultValue?: string;
  className?: string;
  sm?: boolean;
} & { rows?: TextareaProps["rows"] };

const TextProperty = (props: TextPropertyProps) => {
  const { className, markdown, sm = false, rows, ...delegated } = props;

  const { property, section } = useDataCardProperty(delegated);

  if (!property.visible) {
    return null;
  }

  if (section.isEdited && !property.readonly) {
    return (
      <DataCard.Property property={property}>
        {markdown ? (
          <Textarea
            className="w-full"
            value={property.formValue}
            onChange={(e) => property.setValue(e.target.value)}
            required={property.required}
            rows={rows}
            readOnly={property.readonly}
          />
        ) : (
          <Input
            fullWidth
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
          <MarkdownViewer sm={sm} markdown={property.displayValue} />
        ) : (
          <div className={clsx("prose text-sm text-gray-900", className)}>
            {property.displayValue ?? property.defaultValue}
          </div>
        )}
      </DataCard.Property>
    );
  }
};

export default TextProperty;
