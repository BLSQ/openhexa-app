import Badge, { BadgeProps } from "../Badge";
import { useDataCardProperty } from "./context";
import PropertyDisplay from "./PropertyDisplay";
import { PropertyDefinition } from "./types";

export type BadgeItem = {
  label: string;
  url?: string;
  size?: BadgeProps["size"];
  color?: string;
};
type BadgePropertyProps = PropertyDefinition & {
  prepare?(value: any): BadgeItem[];
};

const BadgeProperty = (props: BadgePropertyProps) => {
  const { prepare, id, accessor, required, readonly, label } = props;

  const { property } = useDataCardProperty<BadgeItem[]>({
    id,
    accessor,
    required,
    readonly,
    label,
  });

  return (
    <PropertyDisplay property={property}>
      <div className="flex flex-wrap items-center gap-1.5">
        {(prepare ? prepare(property.displayValue) : property.displayValue).map(
          (badge, i) => (
            <Badge key={i} size={badge.size}>
              {badge.label}
            </Badge>
          ),
        )}
      </div>
    </PropertyDisplay>
  );
};

export default BadgeProperty;
