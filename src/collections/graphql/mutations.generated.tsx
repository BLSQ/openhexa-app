import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type DeleteCollectionMutationVariables = Types.Exact<{
  input: Types.DeleteCollectionInput;
}>;


export type DeleteCollectionMutation = { __typename?: 'Mutation', deleteCollection: { __typename?: 'DeleteCollectionResult', success: boolean, errors: Array<Types.DeleteCollectionError> } };

export type DeleteCollectionElementMutationVariables = Types.Exact<{
  input: Types.DeleteCollectionElementInput;
}>;


export type DeleteCollectionElementMutation = { __typename?: 'Mutation', deleteCollectionElement: { __typename?: 'DeleteCollectionElementResult', success: boolean, errors: Array<Types.DeleteCollectionElementError> } };

export type UpdateCollectionMutationVariables = Types.Exact<{
  input: Types.UpdateCollectionInput;
}>;


export type UpdateCollectionMutation = { __typename?: 'Mutation', updateCollection: { __typename?: 'UpdateCollectionResult', success: boolean, errors: Array<Types.CreateCollectionError>, collection?: { __typename?: 'Collection', id: string, name: string, description?: string | null, summary?: string | null } | null } };


export const DeleteCollectionDocument = gql`
    mutation DeleteCollection($input: DeleteCollectionInput!) {
  deleteCollection(input: $input) {
    success
    errors
  }
}
    `;
export type DeleteCollectionMutationFn = Apollo.MutationFunction<DeleteCollectionMutation, DeleteCollectionMutationVariables>;

/**
 * __useDeleteCollectionMutation__
 *
 * To run a mutation, you first call `useDeleteCollectionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteCollectionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteCollectionMutation, { data, loading, error }] = useDeleteCollectionMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeleteCollectionMutation(baseOptions?: Apollo.MutationHookOptions<DeleteCollectionMutation, DeleteCollectionMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeleteCollectionMutation, DeleteCollectionMutationVariables>(DeleteCollectionDocument, options);
      }
export type DeleteCollectionMutationHookResult = ReturnType<typeof useDeleteCollectionMutation>;
export type DeleteCollectionMutationResult = Apollo.MutationResult<DeleteCollectionMutation>;
export type DeleteCollectionMutationOptions = Apollo.BaseMutationOptions<DeleteCollectionMutation, DeleteCollectionMutationVariables>;
export const DeleteCollectionElementDocument = gql`
    mutation DeleteCollectionElement($input: DeleteCollectionElementInput!) {
  deleteCollectionElement(input: $input) {
    success
    errors
  }
}
    `;
export type DeleteCollectionElementMutationFn = Apollo.MutationFunction<DeleteCollectionElementMutation, DeleteCollectionElementMutationVariables>;

/**
 * __useDeleteCollectionElementMutation__
 *
 * To run a mutation, you first call `useDeleteCollectionElementMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteCollectionElementMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteCollectionElementMutation, { data, loading, error }] = useDeleteCollectionElementMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeleteCollectionElementMutation(baseOptions?: Apollo.MutationHookOptions<DeleteCollectionElementMutation, DeleteCollectionElementMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeleteCollectionElementMutation, DeleteCollectionElementMutationVariables>(DeleteCollectionElementDocument, options);
      }
export type DeleteCollectionElementMutationHookResult = ReturnType<typeof useDeleteCollectionElementMutation>;
export type DeleteCollectionElementMutationResult = Apollo.MutationResult<DeleteCollectionElementMutation>;
export type DeleteCollectionElementMutationOptions = Apollo.BaseMutationOptions<DeleteCollectionElementMutation, DeleteCollectionElementMutationVariables>;
export const UpdateCollectionDocument = gql`
    mutation UpdateCollection($input: UpdateCollectionInput!) {
  updateCollection(input: $input) {
    collection {
      id
      name
      description
      summary
    }
    success
    errors
  }
}
    `;
export type UpdateCollectionMutationFn = Apollo.MutationFunction<UpdateCollectionMutation, UpdateCollectionMutationVariables>;

/**
 * __useUpdateCollectionMutation__
 *
 * To run a mutation, you first call `useUpdateCollectionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateCollectionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateCollectionMutation, { data, loading, error }] = useUpdateCollectionMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateCollectionMutation(baseOptions?: Apollo.MutationHookOptions<UpdateCollectionMutation, UpdateCollectionMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateCollectionMutation, UpdateCollectionMutationVariables>(UpdateCollectionDocument, options);
      }
export type UpdateCollectionMutationHookResult = ReturnType<typeof useUpdateCollectionMutation>;
export type UpdateCollectionMutationResult = Apollo.MutationResult<UpdateCollectionMutation>;
export type UpdateCollectionMutationOptions = Apollo.BaseMutationOptions<UpdateCollectionMutation, UpdateCollectionMutationVariables>;