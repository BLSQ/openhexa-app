import clsx from "clsx";
import { useDataCardProperty } from "./context";
import DataCard from "core/components/DataCard";
import MarkdownEditor from "core/components/MarkdownEditor/MarkdownEditor";
import MarkdownViewer from "core/components/MarkdownViewer";
import { PropertyDefinition } from "./types";

type MarkdownPropertyProps = PropertyDefinition & {
  className?: string;
  defaultValue?: string;
};

const MarkdownProperty = (props: MarkdownPropertyProps) => {
  const { className, defaultValue = "", ...delegated } = props;
  const { property, section } = useDataCardProperty(delegated);

  if (!property.visible) return null;

  const markdownValue =
    typeof property.formValue === "string" ? property.formValue : defaultValue;

  return (
    <DataCard.Property property={property}>
      {section.isEdited && !property.readonly ? (
        <div className={clsx("bg-white", className)}>
          <MarkdownEditor
            sm
            markdown={markdownValue}
            onChange={(markdown) => property.setValue(markdown)}
          />
        </div>
      ) : (
        <MarkdownViewer sm markdown={property.displayValue || defaultValue} />
      )}
    </DataCard.Property>
  );
};

export default MarkdownProperty;
