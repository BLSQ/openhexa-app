import DataCard from "core/components/DataCard";
import { useTranslation } from "next-i18next";
import React from "react";
import ManageCollectionItemDialog from "../ManageCollectionItemDialog";

type CollectionsSectionProps = {
  collections: any;
  element: React.ComponentProps<typeof ManageCollectionItemDialog>["element"];
};

const CollectionsSection = (props: CollectionsSectionProps) => {
  const { element } = props;
  const { t } = useTranslation();
  return <DataCard.Section title={t("Manage collections")}></DataCard.Section>;
};

export default CollectionsSection;
