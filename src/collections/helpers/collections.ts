import { gql } from "@apollo/client";
import { getApolloClient } from "core/helpers/apollo";
import { CreateCollectionInput } from "graphql-types";
import {
  CreateCollectionMutationVariables,
  CreateCollectionMutation,
  AddDhis2DataElementToCollectionMutation,
  AddDhis2DataElementToCollectionMutationVariables,
  AddS3ObjectToCollectionMutation,
  AddS3ObjectToCollectionMutationVariables,
} from "./collections.generated";

export async function addToCollection(
  collectionId: string,
  element: { id: string; __typename: string }
) {
  const client = getApolloClient();
  switch (element.__typename) {
    case "DHIS2DataElement": {
      const { data } = await client.mutate<
        AddDhis2DataElementToCollectionMutation,
        AddDhis2DataElementToCollectionMutationVariables
      >({
        mutation: gql`
          mutation addDHIS2DataElementToCollection(
            $input: AddDHIS2DataElementToCollectionInput!
          ) {
            addToCollection: addDHIS2DataElementToCollection(input: $input) {
              success
              errors
            }
          }
        `,
        variables: { input: { id: element.id, collectionId } },
      });
      return data?.addToCollection.success;
    }
    case "S3Object": {
      const { data } = await client.mutate<
        AddS3ObjectToCollectionMutation,
        AddS3ObjectToCollectionMutationVariables
      >({
        mutation: gql`
          mutation addS3ObjectToCollection(
            $input: AddS3ObjectToCollectionInput!
          ) {
            addToCollection: addS3ObjectToCollection(input: $input) {
              success
              errors
            }
          }
        `,
        variables: { input: { id: element.id, collectionId } },
      });
      return data?.addToCollection.success;
    }
  }
}

export async function removeFromCollection(
  collectionId: string,
  element: { id: string; __typename: string }
) {
  const client = getApolloClient();
  switch (element.__typename) {
    case "DHIS2DataElement": {
      const { data } = await client.mutate({
        mutation: gql`
          mutation removeDHIS2DataElementFromCollection(
            $input: RemoveDHIS2DataElementFromCollectionInput!
          ) {
            removeFromCollection: removeDHIS2DataElementFromCollection(
              input: $input
            ) {
              success
              errors
            }
          }
        `,
        variables: {
          input: {
            collectionId,
            id: element.id,
          },
        },
      });
      return data?.removeFromCollection.success;
    }
    case "S3Object": {
      const { data } = await client.mutate({
        mutation: gql`
          mutation removeS3ObjectFromCollection(
            $input: RemoveS3ObjectFromCollectionInput!
          ) {
            removeFromCollection: removeS3ObjectFromCollection(input: $input) {
              success
              errors
            }
          }
        `,
        variables: {
          input: {
            collectionId,
            id: element.id,
          },
        },
      });
      return data?.removeFromCollection.success;
    }
  }
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
