import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type AddDhis2DataElementToCollectionMutationVariables = Types.Exact<{
  input: Types.AddDhis2DataElementToCollectionInput;
}>;


export type AddDhis2DataElementToCollectionMutation = { __typename?: 'Mutation', addToCollection: { __typename?: 'AddDHIS2DataElementToCollectionResult', success: boolean, errors: Array<Types.AddDhis2DataElementToCollectionError> } };

export type AddS3ObjectToCollectionMutationVariables = Types.Exact<{
  input: Types.AddS3ObjectToCollectionInput;
}>;


export type AddS3ObjectToCollectionMutation = { __typename?: 'Mutation', addToCollection: { __typename?: 'AddS3ObjectToCollectionResult', success: boolean, errors: Array<Types.AddS3ObjectToCollectionError> } };

export type RemoveDhis2DataElementFromCollectionMutationVariables = Types.Exact<{
  input: Types.RemoveDhis2DataElementFromCollectionInput;
}>;


export type RemoveDhis2DataElementFromCollectionMutation = { __typename?: 'Mutation', removeFromCollection: { __typename?: 'RemoveDHIS2DataElementFromCollectionResult', success: boolean, errors: Array<Types.RemoveDhis2DataElementFromCollectionError> } };

export type RemoveS3ObjectFromCollectionMutationVariables = Types.Exact<{
  input: Types.RemoveS3ObjectFromCollectionInput;
}>;


export type RemoveS3ObjectFromCollectionMutation = { __typename?: 'Mutation', removeFromCollection: { __typename?: 'RemoveS3ObjectFromCollectionResult', success: boolean, errors: Array<Types.RemoveS3ObjectFromCollectionError> } };

export type CreateCollectionMutationVariables = Types.Exact<{
  input: Types.CreateCollectionInput;
}>;


export type CreateCollectionMutation = { __typename?: 'Mutation', createCollection: { __typename?: 'CreateCollectionResult', success: boolean, errors: Array<Types.CreateCollectionError>, collection?: { __typename?: 'Collection', id: string, name: string } | null } };


export const AddDhis2DataElementToCollectionDocument = gql`
    mutation addDHIS2DataElementToCollection($input: AddDHIS2DataElementToCollectionInput!) {
  addToCollection: addDHIS2DataElementToCollection(input: $input) {
    success
    errors
  }
}
    `;
export type AddDhis2DataElementToCollectionMutationFn = Apollo.MutationFunction<AddDhis2DataElementToCollectionMutation, AddDhis2DataElementToCollectionMutationVariables>;

/**
 * __useAddDhis2DataElementToCollectionMutation__
 *
 * To run a mutation, you first call `useAddDhis2DataElementToCollectionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useAddDhis2DataElementToCollectionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [addDhis2DataElementToCollectionMutation, { data, loading, error }] = useAddDhis2DataElementToCollectionMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useAddDhis2DataElementToCollectionMutation(baseOptions?: Apollo.MutationHookOptions<AddDhis2DataElementToCollectionMutation, AddDhis2DataElementToCollectionMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<AddDhis2DataElementToCollectionMutation, AddDhis2DataElementToCollectionMutationVariables>(AddDhis2DataElementToCollectionDocument, options);
      }
export type AddDhis2DataElementToCollectionMutationHookResult = ReturnType<typeof useAddDhis2DataElementToCollectionMutation>;
export type AddDhis2DataElementToCollectionMutationResult = Apollo.MutationResult<AddDhis2DataElementToCollectionMutation>;
export type AddDhis2DataElementToCollectionMutationOptions = Apollo.BaseMutationOptions<AddDhis2DataElementToCollectionMutation, AddDhis2DataElementToCollectionMutationVariables>;
export const AddS3ObjectToCollectionDocument = gql`
    mutation addS3ObjectToCollection($input: AddS3ObjectToCollectionInput!) {
  addToCollection: addS3ObjectToCollection(input: $input) {
    success
    errors
  }
}
    `;
export type AddS3ObjectToCollectionMutationFn = Apollo.MutationFunction<AddS3ObjectToCollectionMutation, AddS3ObjectToCollectionMutationVariables>;

/**
 * __useAddS3ObjectToCollectionMutation__
 *
 * To run a mutation, you first call `useAddS3ObjectToCollectionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useAddS3ObjectToCollectionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [addS3ObjectToCollectionMutation, { data, loading, error }] = useAddS3ObjectToCollectionMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useAddS3ObjectToCollectionMutation(baseOptions?: Apollo.MutationHookOptions<AddS3ObjectToCollectionMutation, AddS3ObjectToCollectionMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<AddS3ObjectToCollectionMutation, AddS3ObjectToCollectionMutationVariables>(AddS3ObjectToCollectionDocument, options);
      }
export type AddS3ObjectToCollectionMutationHookResult = ReturnType<typeof useAddS3ObjectToCollectionMutation>;
export type AddS3ObjectToCollectionMutationResult = Apollo.MutationResult<AddS3ObjectToCollectionMutation>;
export type AddS3ObjectToCollectionMutationOptions = Apollo.BaseMutationOptions<AddS3ObjectToCollectionMutation, AddS3ObjectToCollectionMutationVariables>;
export const RemoveDhis2DataElementFromCollectionDocument = gql`
    mutation removeDHIS2DataElementFromCollection($input: RemoveDHIS2DataElementFromCollectionInput!) {
  removeFromCollection: removeDHIS2DataElementFromCollection(input: $input) {
    success
    errors
  }
}
    `;
export type RemoveDhis2DataElementFromCollectionMutationFn = Apollo.MutationFunction<RemoveDhis2DataElementFromCollectionMutation, RemoveDhis2DataElementFromCollectionMutationVariables>;

/**
 * __useRemoveDhis2DataElementFromCollectionMutation__
 *
 * To run a mutation, you first call `useRemoveDhis2DataElementFromCollectionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useRemoveDhis2DataElementFromCollectionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [removeDhis2DataElementFromCollectionMutation, { data, loading, error }] = useRemoveDhis2DataElementFromCollectionMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useRemoveDhis2DataElementFromCollectionMutation(baseOptions?: Apollo.MutationHookOptions<RemoveDhis2DataElementFromCollectionMutation, RemoveDhis2DataElementFromCollectionMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<RemoveDhis2DataElementFromCollectionMutation, RemoveDhis2DataElementFromCollectionMutationVariables>(RemoveDhis2DataElementFromCollectionDocument, options);
      }
export type RemoveDhis2DataElementFromCollectionMutationHookResult = ReturnType<typeof useRemoveDhis2DataElementFromCollectionMutation>;
export type RemoveDhis2DataElementFromCollectionMutationResult = Apollo.MutationResult<RemoveDhis2DataElementFromCollectionMutation>;
export type RemoveDhis2DataElementFromCollectionMutationOptions = Apollo.BaseMutationOptions<RemoveDhis2DataElementFromCollectionMutation, RemoveDhis2DataElementFromCollectionMutationVariables>;
export const RemoveS3ObjectFromCollectionDocument = gql`
    mutation removeS3ObjectFromCollection($input: RemoveS3ObjectFromCollectionInput!) {
  removeFromCollection: removeS3ObjectFromCollection(input: $input) {
    success
    errors
  }
}
    `;
export type RemoveS3ObjectFromCollectionMutationFn = Apollo.MutationFunction<RemoveS3ObjectFromCollectionMutation, RemoveS3ObjectFromCollectionMutationVariables>;

/**
 * __useRemoveS3ObjectFromCollectionMutation__
 *
 * To run a mutation, you first call `useRemoveS3ObjectFromCollectionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useRemoveS3ObjectFromCollectionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [removeS3ObjectFromCollectionMutation, { data, loading, error }] = useRemoveS3ObjectFromCollectionMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useRemoveS3ObjectFromCollectionMutation(baseOptions?: Apollo.MutationHookOptions<RemoveS3ObjectFromCollectionMutation, RemoveS3ObjectFromCollectionMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<RemoveS3ObjectFromCollectionMutation, RemoveS3ObjectFromCollectionMutationVariables>(RemoveS3ObjectFromCollectionDocument, options);
      }
export type RemoveS3ObjectFromCollectionMutationHookResult = ReturnType<typeof useRemoveS3ObjectFromCollectionMutation>;
export type RemoveS3ObjectFromCollectionMutationResult = Apollo.MutationResult<RemoveS3ObjectFromCollectionMutation>;
export type RemoveS3ObjectFromCollectionMutationOptions = Apollo.BaseMutationOptions<RemoveS3ObjectFromCollectionMutation, RemoveS3ObjectFromCollectionMutationVariables>;
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