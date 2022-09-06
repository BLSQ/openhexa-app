import { gql, useLazyQuery } from "@apollo/client";
import {
  addToCollection,
  removeFromCollection,
} from "collections/helpers/collections";
import useCollectionForm from "collections/hooks/useCollectionForm";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Spinner from "core/components/Spinner";
import Switch from "core/components/Switch";
import Tabs from "core/components/Tabs";
import CountryBadge from "core/features/CountryBadge";
import { AlertType, displayAlert } from "core/helpers/alert";
import { useTranslation } from "next-i18next";
import { useCallback, useEffect, useMemo, useState } from "react";
import CollectionPartialForm from "./CollectionPartialForm";
import {
  ManageCollectionItemDialogQuery,
  ManageCollectionItemDialogQueryVariables,
} from "./ManageCollectionItemDialog.generated";

type ManageCollectionItemDialogProps = {
  onClose: () => void;
  open: boolean;
  element: { id: string; __typename: string };
};

const ManageCollectionItemDialog = (props: ManageCollectionItemDialogProps) => {
  const { t } = useTranslation();
  const { onClose, open, element } = props;
  const [loading, setLoading] = useState(false);
  const collectionForm = useCollectionForm();
  const [operations, setOperations] = useState<{
    [key: string]: "add" | "delete";
  }>({});
  const [currentTabIndex, setTabIndex] = useState(0);
  const [fetch, { data, loading: loadingData }] = useLazyQuery<
    ManageCollectionItemDialogQuery,
    ManageCollectionItemDialogQueryVariables
  >(gql`
    query ManageCollectionItemDialog {
      collections {
        items {
          id
          name
          summary
          elements {
            items {
              id
              ... on S3ObjectCollectionElement {
                element {
                  id
                }
              }
              ... on DHIS2DataElementCollectionElement {
                element {
                  id
                }
              }
            }
          }
          countries {
            ...CountryBadge_country
          }
        }
      }
    }
    ${CountryBadge.fragments.country}
  `);

  useEffect(() => {
    if (open) {
      collectionForm.resetForm();
      fetch();
    } else {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, fetch]);

  const onTabChange = useCallback(
    (index: number) => {
      collectionForm.resetForm();
      setTabIndex(index);
    },
    [setTabIndex, collectionForm]
  );

  const isElementInCollection = useCallback(
    (collection: any) => {
      if (!element) return false;
      if (collection.id in operations) {
        return operations[collection.id] === "add";
      }
      return collection.elements.items.some(
        (collectionElement: any) => collectionElement.element.id === element.id
      );
    },
    [operations, element]
  );

  const onChangeCollectionSwitch = (checked: boolean, collection: any) => {
    const isInServerCollection = collection.elements.items.some(
      (collectionElement: any) => collectionElement.element.id === element.id
    );

    if (checked) {
      operations[collection.id] = "add";
      if (isInServerCollection) {
        delete operations[collection.id];
      }
    } else {
      operations[collection.id] = "delete";
      if (!isInServerCollection) {
        delete operations[collection.id];
      }
    }
    setOperations({ ...operations });
  };

  async function onSave() {
    setLoading(true);
    if (currentTabIndex === 0) {
      // We just need to add / remove the element
      const promises = await Promise.all(
        Object.entries(operations).map(async ([collectionId, operation]) => {
          if (operation === "add") {
            return addToCollection(collectionId, element);
          } else if (operation === "delete") {
            return removeFromCollection(collectionId, element);
          }
        })
      );
      setLoading(false);
      if (!promises.every(Boolean)) {
        displayAlert(t("Unable to set collections"), AlertType.error);
      } else {
        onClose();
      }
    } else {
      // We need to create the new collection and add the element to it
      try {
        const collection = await collectionForm.handleSubmit();
        if (collection) {
          await addToCollection(collection.id, element);
        }
        // onClose();
      } catch (exc: any) {
        displayAlert((exc as Error).message, AlertType.error);
      } finally {
        setLoading(false);
      }
    }
  }

  const isOpen = useMemo(() => {
    return open && Boolean(data?.collections) && !loadingData;
  }, [open, data, loadingData]);

  return (
    <Dialog maxWidth="max-w-2xl" open={isOpen} onClose={onClose}>
      <Dialog.Title onClose={onClose}>{t("Manage collection")}</Dialog.Title>
      <Dialog.Content>
        {data?.collections && (
          <Tabs onChange={onTabChange}>
            <Tabs.Tab className="mt-4" label={t("Existing collections")}>
              <p className="px-2 text-gray-500">
                {t(
                  "Add or remove this element from the collections below by using the switch"
                )}
              </p>
              <div className="max-h-96 divide-y-2 overflow-y-auto">
                {data.collections.items.map((collection) => (
                  <div
                    key={collection.id}
                    className="flex items-center gap-4 py-4 px-2"
                  >
                    <div className="flex-1">
                      <div className="truncate font-medium">
                        {collection.name}
                      </div>
                      <div
                        className="truncate pt-1 text-sm text-gray-500"
                        title={collection.summary ?? ""}
                      >
                        {collection.summary}
                      </div>
                    </div>

                    {collection.countries.length > 0 && (
                      <div
                        title={collection.countries
                          .map((c) => c.name)
                          .join(", ")}
                      >
                        <CountryBadge country={collection.countries[0]} />
                        {collection.countries.length > 1 && (
                          <span className="ml-2 text-sm">
                            +{collection.countries.length - 1}
                          </span>
                        )}
                      </div>
                    )}
                    <Switch
                      checked={isElementInCollection(collection)}
                      onChange={(checked) =>
                        onChangeCollectionSwitch(checked, collection)
                      }
                    />
                  </div>
                ))}
              </div>
            </Tabs.Tab>
            <Tabs.Tab className="mt-4" label={t("Create a collection")}>
              <CollectionPartialForm form={collectionForm} />
            </Tabs.Tab>
          </Tabs>
        )}
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" onClick={onClose}>
          {t("Cancel")}
        </Button>
        <Button
          disabled={
            loading || (currentTabIndex === 1 ? !collectionForm.isValid : false)
          }
          onClick={onSave}
        >
          {loading && <Spinner className="mr-1" size="xs" />}
          {t("Done")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

export default ManageCollectionItemDialog;
