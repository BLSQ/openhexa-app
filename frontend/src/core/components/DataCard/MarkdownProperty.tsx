import clsx from "clsx";
import { useDataCardProperty } from "./context";
import DataCard from "../../../core/components/DataCard";
import MarkdownEditor from "../../../core/components/MarkdownEditor/MarkdownEditor";
import MarkdownViewer from "../../../core/components/MarkdownViewer";
import { PropertyDefinition } from "./types";
import Block from "../Block";

type MarkdownPropertyProps = PropertyDefinition & {
  className?: string;
};

const MarkdownProperty = (props: MarkdownPropertyProps) => {
  const { className, ...delegated } = props;
  const { property, section } = useDataCardProperty(delegated);

  if (!property.visible) return null;

  return (
    <DataCard.Property property={property}>
      {section.isEdited && !property.readonly ? (
        <div className={clsx("bg-white", className)}>
          <MarkdownEditor
            markdown={property.formValue || ""}
            onChange={(markdown) => property.setValue(markdown)}
          />
        </div>
      ) : (
        <Block>
          <Block.Content>
            <MarkdownViewer markdown={property.displayValue || ""} />
          </Block.Content>
        </Block>
      )}
    </DataCard.Property>
  );
};

export default MarkdownProperty;
