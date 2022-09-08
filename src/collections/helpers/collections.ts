import { gql } from "@apollo/client";
import {
  DeleteCollectionMutation,
  DeleteCollectionMutationVariables,
} from "collections/graphql/mutations.generated";
import { getApolloClient } from "core/helpers/apollo";
import { CreateCollectionInput } from "graphql-types";
import {
  CreateCollectionMutation,
  CreateCollectionMutationVariables,
} from "./collections.generated";

export async function addToCollection(
  collectionId: string,
  element: { id: string; app: string; model: string }
) {
  const client = getApolloClient();
  return client.mutate({
    mutation: gql`
      mutation createCollectionElement($input: CreateCollectionElementInput!) {
        createCollectionElement(input: $input) {
          success
          errors
        }
      }
    `,
    variables: {
      input: {
        collectionId,
        objectId: element.id,
        app: element.app,
        model: element.model,
      },
    },
  });
}

export async function removeFromCollection(elementId: string) {
  const client = getApolloClient();
  const { data } = await client.mutate({
    mutation: gql`
      mutation deleteCollectionElement($input: DeleteCollectionElementInput!) {
        deleteCollectionElement(input: $input) {
          success
          errors
        }
      }
    `,
    variables: {
      input: { id: elementId },
    },
    update(cache) {
      const normalizedId = cache.identify({
        id: elementId,
        __typename: "CollectionElement",
      });

      cache.evict({ id: normalizedId });
      cache.gc();
    },
  });

  return data?.deleteCollectionElement.success;
}

export async function createCollection(input: CreateCollectionInput) {
  const client = getApolloClient();
  const { data } = await client.mutate<
    CreateCollectionMutation,
    CreateCollectionMutationVariables
  >({
    mutation: gql`
      mutation CreateCollection($input: CreateCollectionInput!) {
        createCollection(input: $input) {
          success
          errors
          collection {
            id
            name
          }
        }
      }
    `,
    variables: { input },
  });

  if (!data?.createCollection.collection) {
    throw new Error("Unable to create collection.");
  }

  return data?.createCollection.collection;
}

export async function deleteCollection(collectionId: string) {
  const client = getApolloClient();
  const { data } = await client.mutate<
    DeleteCollectionMutation,
    DeleteCollectionMutationVariables
  >({
    mutation: gql`
      mutation DeleteCollection($input: DeleteCollectionInput!) {
        deleteCollection(input: $input) {
          success
          errors
        }
      }
    `,
    variables: { input: { id: collectionId } },
    update(cache) {
      const normalizedId = cache.identify({
        id: collectionId,
        __typename: "Collection",
      });

      cache.evict({ id: normalizedId });
      cache.gc();
    },
  });

  if (!data?.deleteCollection.success) {
    throw new Error("Impossible to delete collection");
  }
}
