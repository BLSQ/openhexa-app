import { gql } from "@apollo/client";
import {
  DocumentRemoveIcon,
  FolderRemoveIcon,
  TrashIcon,
} from "@heroicons/react/outline";
import Button from "core/components/Button";
import { BaseColumn } from "core/components/DataGrid";
import ChevronLinkColumn from "core/components/DataGrid/ChevronLinkColumn";
import DataGrid from "core/components/DataGrid/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import { useTranslation } from "next-i18next";
import CollectionElementDeleteTrigger from "./CollectionElementDeleteTrigger";
import {
  CollectionElementsTable_CollectionFragment,
  CollectionElementsTable_ElementFragment,
} from "./CollectionElementsTable.generated";

type CollectionElementsTableProps = {
  elements: CollectionElementsTable_ElementFragment[];
  collection: CollectionElementsTable_CollectionFragment;
  isEditing?: boolean;
};

const CollectionElementsTable = (props: CollectionElementsTableProps) => {
  const { elements, collection, isEditing = false } = props;
  const { t } = useTranslation();

  return (
    <DataGrid
      data={elements}
      sortable
      defaultPageSize={10}
      totalItems={elements.length}
    >
      <TextColumn
        label={t("Name")}
        textPath="name"
        subtextPath="type"
        minWidth={300}
        textClassName="text-gray-600 font-medium"
      />
      <DateColumn label={t("Created at")} accessor="createdAt" />
      <DateColumn label={t("Updated at")} accessor="updatedAt" />
      {isEditing ? (
        <BaseColumn<CollectionElementsTable_ElementFragment> id="actions">
          {(value) => (
            <div className="flex w-full justify-end">
              <CollectionElementDeleteTrigger
                collection={collection}
                element={value}
              >
                {({ onClick }) => (
                  <Button
                    onClick={onClick}
                    size="sm"
                    variant="secondary"
                    leadingIcon={<TrashIcon className="w-4" />}
                  >
                    {t("Remove")}
                  </Button>
                )}
              </CollectionElementDeleteTrigger>
            </div>
          )}
        </BaseColumn>
      ) : (
        <ChevronLinkColumn
          hideLabel
          accessor="url"
          url={(value: any) => ({
            pathname: value,
          })}
        />
      )}
    </DataGrid>
  );
};

CollectionElementsTable.fragments = {
  collection: gql`
    fragment CollectionElementsTable_collection on Collection {
      id
      ...CollectionElementDeleteTrigger_collection
    }
    ${CollectionElementDeleteTrigger.fragments.collection}
  `,
  element: gql`
    fragment CollectionElementsTable_element on CollectionElement {
      ...CollectionElementDeleteTrigger_element
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
    ${CollectionElementDeleteTrigger.fragments.element}
  `,
};

export default CollectionElementsTable;
