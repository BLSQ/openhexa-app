import { gql } from "@apollo/client";
import ChevronLinkColumn from "core/components/DataGrid/ChevronLinkColumn";
import DataGrid from "core/components/DataGrid/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import { useTranslation } from "next-i18next";
import { CollectionElementsTable_ElementFragment } from "./CollectionElementsTable.generated";

type CollectionElementsTableProps = {
  elements: CollectionElementsTable_ElementFragment[];
};

const CollectionElementsTable = (props: CollectionElementsTableProps) => {
  const { elements } = props;
  const { t } = useTranslation();

  return (
    <DataGrid data={elements}>
      <TextColumn
        label={t("Name")}
        textPath="name"
        subtextPath="type"
        minWidth={300}
        textClassName="text-gray-600 font-medium"
      />
      <DateColumn label={t("Created at")} accessor="createdAt" />
      <DateColumn label={t("Updated at")} accessor="updatedAt" />
      <ChevronLinkColumn
        hideLabel
        accessor="url"
        url={(value: any) => ({
          pathname: value,
        })}
      />
    </DataGrid>
  );
};

CollectionElementsTable.fragments = {
  element: gql`
    fragment CollectionElementsTable_element on CollectionElement {
      id
      createdAt
      updatedAt
      name
      type
      app
      model
      url
      objectId
    }
  `,
};

export default CollectionElementsTable;
