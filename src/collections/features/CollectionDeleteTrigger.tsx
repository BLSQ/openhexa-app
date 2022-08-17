import { gql, useMutation } from "@apollo/client";
import {
  DeleteCollectionDocument,
  useDeleteCollectionMutation,
} from "collections/graphql/mutations.generated";
import useCacheKey from "core/hooks/useCacheKey";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { ReactNode, useCallback } from "react";
import { ReactElement } from "react-markdown/lib/react-markdown";
import { CollectionDeleteTrigger_CollectionFragment } from "./CollectionDeleteTrigger.generated";

type CollectionDeleteTriggerProps = {
  collection: CollectionDeleteTrigger_CollectionFragment;
  children: ({ onClick }: { onClick: () => void }) => ReactElement;
  confirmMessage?: string;
};

const CollectionDeleteTrigger = (props: CollectionDeleteTriggerProps) => {
  const { t } = useTranslation();
  const {
    collection,
    children,
    confirmMessage = t(
      'Are you sure you want to delete the collection "{{name}}"?',
      {
        name: collection.name,
      }
    ),
  } = props;
  const router = useRouter();
  const [deleteCollection] = useDeleteCollectionMutation();

  const clearCache = useCacheKey(["collections", collection.id]);

  const onClick = useCallback(async () => {
    if (window.confirm(confirmMessage)) {
      await deleteCollection({ variables: { input: { id: collection.id } } });
      clearCache();
      if (
        router.asPath.startsWith(
          `/collections/${encodeURIComponent(collection.id)}`
        )
      ) {
        router.push(`/collections`);
      }
    }
  }, [collection, clearCache, router, deleteCollection, confirmMessage]);

  if (!collection.authorizedActions.canDelete) {
    return null;
  }
  return children({ onClick });
};

CollectionDeleteTrigger.fragments = {
  collection: gql`
    fragment CollectionDeleteTrigger_collection on Collection {
      id
      name
      authorizedActions {
        canDelete
      }
    }
  `,
};

export default CollectionDeleteTrigger;
