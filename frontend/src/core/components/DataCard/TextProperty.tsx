import clsx from "clsx";
import MarkdownViewer from "../MarkdownViewer";
import Input from "../forms/Input";
import Textarea from "../forms/Textarea";
import DataCard from "./DataCard";
import { useDataCardProperty } from "./context";
import { PropertyDefinition } from "./types";
import { TextareaProps } from "../forms/Textarea/Textarea";
import { ChangeEvent, ReactNode } from "react";

type TextPropertyProps = PropertyDefinition & {
  markdown?: boolean;
  defaultValue?: string;
  placeholder?: string;
  className?: string;
  sm?: boolean;
  hint?: ReactNode;
  onChange?: (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
} & { rows?: TextareaProps["rows"] };

const TextProperty = (props: TextPropertyProps) => {
  const {
    className,
    markdown,
    sm = false,
    rows,
    onChange,
    defaultValue,
    placeholder,
    hint,
    ...delegated
  } = props;

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
            placeholder={placeholder}
            value={property.formValue}
            onChange={(e) => {
              property.setValue(e.target.value);
              if (onChange) onChange(e);
            }}
            required={property.required}
            rows={rows}
            readOnly={property.readonly}
          />
        ) : (
          <Input
            fullWidth
            value={property.formValue ?? ""}
            placeholder={placeholder}
            onChange={(e) => {
              property.setValue(e.target.value);
              if (onChange) onChange(e);
            }}
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
          <div
            className={clsx(
              "prose text-sm",
              property.displayValue ? "text-gray-900" : "text-gray-500 italic",
              className,
            )}
          >
            {property.displayValue || defaultValue}
          </div>
        )}
        {hint && <p className="mt-1 text-xs text-amber-700">{hint}</p>}
      </DataCard.Property>
    );
  }
};

export default TextProperty;
