import React from "react";
import { getLabel, getTypeIcon, TypeName } from "./mapper";
import { useTranslation } from "next-i18next";
import { FileType } from "graphql/types";

type TypeBadgeProps = {
  typeName: TypeName;
  type?: FileType;
};

const TypeBadge = ({ typeName, type }: TypeBadgeProps) => {
  const { t } = useTranslation();
  const Icon = getTypeIcon(typeName, type);
  return (
    <div className="flex">
      <Icon className="h-5 w-5" />
      <div className="ml-1">{getLabel(typeName, t, type)}</div>
    </div>
  );
};

export default TypeBadge;
