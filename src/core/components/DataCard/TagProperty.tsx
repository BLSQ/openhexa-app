import Tag from "core/features/Tag";
import { Tag_TagFragment } from "core/features/Tag.generated";
import { useDataCardProperty } from "./context";
import DataCard from "../DataCard";
import { PropertyDefinition } from "./types";

type TagPropertyProps = PropertyDefinition;

const TagProperty = (props: TagPropertyProps) => {
  const { defaultValue } = props;
  const { property } = useDataCardProperty<Tag_TagFragment[]>(props);

  return (
    <DataCard.Property property={property}>
      <div className="flex flex-wrap items-center gap-1.5">
        {property.displayValue.length === 0 && defaultValue}
        {property.displayValue.map((tag, i) => (
          <Tag key={i} tag={tag} />
        ))}
      </div>
    </DataCard.Property>
  );
};

export default TagProperty;
