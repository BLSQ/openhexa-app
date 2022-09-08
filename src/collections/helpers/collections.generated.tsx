import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type CreateCollectionElementMutationVariables = Types.Exact<{
  input: Types.CreateCollectionElementInput;
}>;


export type CreateCollectionElementMutation = { __typename?: 'Mutation', createCollectionElement: { __typename?: 'CreateCollectionElementResult', success: boolean, errors: Array<Types.CreateCollectionElementError> } };

export type DeleteCollectionElementMutationVariables = Types.Exact<{
  input: Types.DeleteCollectionElementInput;
}>;


export type DeleteCollectionElementMutation = { __typename?: 'Mutation', deleteCollectionElement: { __typename?: 'DeleteCollectionElementResult', success: boolean, errors: Array<Types.DeleteCollectionElementError> } };

export type CreateCollectionMutationVariables = Types.Exact<{
  input: Types.CreateCollectionInput;
}>;


export type CreateCollectionMutation = { __typename?: 'Mutation', createCollection: { __typename?: 'CreateCollectionResult', success: boolean, errors: Array<Types.CreateCollectionError>, collection?: { __typename?: 'Collection', id: string, name: string } | null } };


export const CreateCollectionElementDocument = gql`
    mutation createCollectionElement($input: CreateCollectionElementInput!) {
  createCollectionElement(input: $input) {
    success
    errors
  }
}
    `;
export type CreateCollectionElementMutationFn = Apollo.MutationFunction<CreateCollectionElementMutation, CreateCollectionElementMutationVariables>;

/**
 * __useCreateCollectionElementMutation__
 *
 * To run a mutation, you first call `useCreateCollectionElementMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateCollectionElementMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createCollectionElementMutation, { data, loading, error }] = useCreateCollectionElementMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useCreateCollectionElementMutation(baseOptions?: Apollo.MutationHookOptions<CreateCollectionElementMutation, CreateCollectionElementMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<CreateCollectionElementMutation, CreateCollectionElementMutationVariables>(CreateCollectionElementDocument, options);
      }
export type CreateCollectionElementMutationHookResult = ReturnType<typeof useCreateCollectionElementMutation>;
export type CreateCollectionElementMutationResult = Apollo.MutationResult<CreateCollectionElementMutation>;
export type CreateCollectionElementMutationOptions = Apollo.BaseMutationOptions<CreateCollectionElementMutation, CreateCollectionElementMutationVariables>;
export const DeleteCollectionElementDocument = gql`
    mutation deleteCollectionElement($input: DeleteCollectionElementInput!) {
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
export const CreateCollectionDocument = gql`
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
    `;
export type CreateCollectionMutationFn = Apollo.MutationFunction<CreateCollectionMutation, CreateCollectionMutationVariables>;

/**
 * __useCreateCollectionMutation__
 *
 * To run a mutation, you first call `useCreateCollectionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateCollectionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createCollectionMutation, { data, loading, error }] = useCreateCollectionMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useCreateCollectionMutation(baseOptions?: Apollo.MutationHookOptions<CreateCollectionMutation, CreateCollectionMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<CreateCollectionMutation, CreateCollectionMutationVariables>(CreateCollectionDocument, options);
      }
export type CreateCollectionMutationHookResult = ReturnType<typeof useCreateCollectionMutation>;
export type CreateCollectionMutationResult = Apollo.MutationResult<CreateCollectionMutation>;
export type CreateCollectionMutationOptions = Apollo.BaseMutationOptions<CreateCollectionMutation, CreateCollectionMutationVariables>;