import React from "react";
import { getLabel, getTypeIcon, TypeName } from "./mapper";
import { useTranslation } from "next-i18next";
import { BucketObjectType } from "graphql/types";

type TypeBadgeProps = {
  typeName: TypeName;
  type?: BucketObjectType;
  name?: string;
};

const TypeBadge = ({ typeName, type, name }: TypeBadgeProps) => {
  const { t } = useTranslation();
  const Icon = getTypeIcon(typeName, type, name);
  return (
    <div className="flex">
      <Icon className="h-5 w-5" />
      <div className="ml-1">{getLabel(typeName, t, type, name)}</div>
    </div>
  );
};

export default TypeBadge;
