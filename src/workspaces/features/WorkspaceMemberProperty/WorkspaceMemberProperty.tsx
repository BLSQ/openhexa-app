import { useDataCardProperty } from "core/components/DataCard/context";
import DataCard from "core/components/DataCard/DataCard";
import { PropertyDefinition } from "core/components/DataCard/types";

import { ensureArray } from "core/helpers/array";
import { useMemo } from "react";
import WorkspaceMemberPicker from "../WorkspaceMemberPicker";
import clsx from "clsx";

type WorkspaceMemberPropertyProps = {
  multiple?: boolean;
  disabled?: boolean;
  slug: string;
  className?: string;
} & PropertyDefinition;

const WorkspaceMemberProperty = (props: WorkspaceMemberPropertyProps) => {
  const { disabled, className, slug, defaultValue, ...delegated } = props;
  const { property, section } = useDataCardProperty(delegated);

  const membersArray = useMemo(
    () => ensureArray(property.displayValue),
    [property],
  );
  return (
    <DataCard.Property property={property}>
      {section.isEdited ? (
        <WorkspaceMemberPicker
          workspaceSlug={slug}
          value={property.formValue ?? []}
          onChange={(v) => property.setValue(v)}
          withPortal
          disabled={disabled}
        />
      ) : (
        <div className={clsx("text-sm text-gray-900", className)}>
          {membersArray.length === 0 && defaultValue}
          {membersArray.map((member, i) => member.user.displayName).join(", ")}
        </div>
      )}
    </DataCard.Property>
  );
};

export default WorkspaceMemberProperty;
