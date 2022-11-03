import { gql } from "@apollo/client";
import { removeFromCollection } from "collections/helpers/collections";
import useCacheKey from "core/hooks/useCacheKey";
import { useTranslation } from "next-i18next";
import { ReactElement, useCallback } from "react";
import {
  CollectionElementDeleteTrigger_CollectionFragment,
  CollectionElementDeleteTrigger_ElementFragment,
} from "./CollectionElementDeleteTrigger.generated";

type CollectionElementDeleteTriggerProps = {
  element: CollectionElementDeleteTrigger_ElementFragment;
  collection: CollectionElementDeleteTrigger_CollectionFragment;
  children: ({ onClick }: { onClick: () => void }) => ReactElement;
  confirmMessage?: string;
};

const CollectionElementDeleteTrigger = (
  props: CollectionElementDeleteTriggerProps
) => {
  const { t } = useTranslation();
  const {
    element,
    children,
    collection,
    confirmMessage = t('Are you sure you want to delete "{{name}}"?', {
      name: element.name,
    }),
  } = props;

  const clearCache = useCacheKey(["collections", collection.id]);

  const onClick = useCallback(async () => {
    if (window.confirm(confirmMessage)) {
      await removeFromCollection(element.id);
      clearCache();
    }
  }, [element, clearCache, confirmMessage]);

  if (!collection.permissions.update) {
    return null;
  }

  return children({ onClick });
};

CollectionElementDeleteTrigger.fragments = {
  collection: gql`
    fragment CollectionElementDeleteTrigger_collection on Collection {
      id
      permissions {
        update
      }
    }
  `,
  element: gql`
    fragment CollectionElementDeleteTrigger_element on CollectionElement {
      id
      name
    }
  `,
};

export default CollectionElementDeleteTrigger;
