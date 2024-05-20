import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type UpdateDatasetMutationVariables = Types.Exact<{
  input: Types.UpdateDatasetInput;
}>;


export type UpdateDatasetMutation = { __typename?: 'Mutation', updateDataset: { __typename?: 'UpdateDatasetResult', success: boolean, errors: Array<Types.UpdateDatasetError>, dataset?: { __typename?: 'Dataset', id: string, name: string, description?: string | null, updatedAt: any } | null } };

export type CreateDatasetVersionMutationVariables = Types.Exact<{
  input: Types.CreateDatasetVersionInput;
}>;


export type CreateDatasetVersionMutation = { __typename?: 'Mutation', createDatasetVersion: { __typename?: 'CreateDatasetVersionResult', success: boolean, errors: Array<Types.CreateDatasetVersionError>, version?: { __typename?: 'DatasetVersion', id: string, name: string } | null } };

export type CreateDatasetVersionFileMutationVariables = Types.Exact<{
  input: Types.CreateDatasetVersionFileInput;
}>;


export type CreateDatasetVersionFileMutation = { __typename?: 'Mutation', createDatasetVersionFile: { __typename?: 'CreateDatasetVersionFileResult', uploadUrl?: string | null, success: boolean, errors: Array<Types.CreateDatasetVersionFileError> } };

export type DeleteDatasetLinkMutationVariables = Types.Exact<{
  input: Types.DeleteDatasetLinkInput;
}>;


export type DeleteDatasetLinkMutation = { __typename?: 'Mutation', deleteDatasetLink: { __typename?: 'DeleteDatasetLinkResult', success: boolean, errors: Array<Types.DeleteDatasetLinkError> } };

export type DeleteDatasetMutationVariables = Types.Exact<{
  input: Types.DeleteDatasetInput;
}>;


export type DeleteDatasetMutation = { __typename?: 'Mutation', deleteDataset: { __typename?: 'DeleteDatasetResult', success: boolean, errors: Array<Types.DeleteDatasetError> } };


export const UpdateDatasetDocument = gql`
    mutation UpdateDataset($input: UpdateDatasetInput!) {
  updateDataset(input: $input) {
    dataset {
      id
      name
      description
      updatedAt
    }
    success
    errors
  }
}
    `;
export type UpdateDatasetMutationFn = Apollo.MutationFunction<UpdateDatasetMutation, UpdateDatasetMutationVariables>;

/**
 * __useUpdateDatasetMutation__
 *
 * To run a mutation, you first call `useUpdateDatasetMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateDatasetMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateDatasetMutation, { data, loading, error }] = useUpdateDatasetMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateDatasetMutation(baseOptions?: Apollo.MutationHookOptions<UpdateDatasetMutation, UpdateDatasetMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateDatasetMutation, UpdateDatasetMutationVariables>(UpdateDatasetDocument, options);
      }
export type UpdateDatasetMutationHookResult = ReturnType<typeof useUpdateDatasetMutation>;
export type UpdateDatasetMutationResult = Apollo.MutationResult<UpdateDatasetMutation>;
export type UpdateDatasetMutationOptions = Apollo.BaseMutationOptions<UpdateDatasetMutation, UpdateDatasetMutationVariables>;
export const CreateDatasetVersionDocument = gql`
    mutation CreateDatasetVersion($input: CreateDatasetVersionInput!) {
  createDatasetVersion(input: $input) {
    version {
      id
      name
    }
    success
    errors
  }
}
    `;
export type CreateDatasetVersionMutationFn = Apollo.MutationFunction<CreateDatasetVersionMutation, CreateDatasetVersionMutationVariables>;

/**
 * __useCreateDatasetVersionMutation__
 *
 * To run a mutation, you first call `useCreateDatasetVersionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateDatasetVersionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createDatasetVersionMutation, { data, loading, error }] = useCreateDatasetVersionMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useCreateDatasetVersionMutation(baseOptions?: Apollo.MutationHookOptions<CreateDatasetVersionMutation, CreateDatasetVersionMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<CreateDatasetVersionMutation, CreateDatasetVersionMutationVariables>(CreateDatasetVersionDocument, options);
      }
export type CreateDatasetVersionMutationHookResult = ReturnType<typeof useCreateDatasetVersionMutation>;
export type CreateDatasetVersionMutationResult = Apollo.MutationResult<CreateDatasetVersionMutation>;
export type CreateDatasetVersionMutationOptions = Apollo.BaseMutationOptions<CreateDatasetVersionMutation, CreateDatasetVersionMutationVariables>;
export const CreateDatasetVersionFileDocument = gql`
    mutation CreateDatasetVersionFile($input: CreateDatasetVersionFileInput!) {
  createDatasetVersionFile(input: $input) {
    uploadUrl
    success
    errors
  }
}
    `;
export type CreateDatasetVersionFileMutationFn = Apollo.MutationFunction<CreateDatasetVersionFileMutation, CreateDatasetVersionFileMutationVariables>;

/**
 * __useCreateDatasetVersionFileMutation__
 *
 * To run a mutation, you first call `useCreateDatasetVersionFileMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateDatasetVersionFileMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createDatasetVersionFileMutation, { data, loading, error }] = useCreateDatasetVersionFileMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useCreateDatasetVersionFileMutation(baseOptions?: Apollo.MutationHookOptions<CreateDatasetVersionFileMutation, CreateDatasetVersionFileMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<CreateDatasetVersionFileMutation, CreateDatasetVersionFileMutationVariables>(CreateDatasetVersionFileDocument, options);
      }
export type CreateDatasetVersionFileMutationHookResult = ReturnType<typeof useCreateDatasetVersionFileMutation>;
export type CreateDatasetVersionFileMutationResult = Apollo.MutationResult<CreateDatasetVersionFileMutation>;
export type CreateDatasetVersionFileMutationOptions = Apollo.BaseMutationOptions<CreateDatasetVersionFileMutation, CreateDatasetVersionFileMutationVariables>;
export const DeleteDatasetLinkDocument = gql`
    mutation DeleteDatasetLink($input: DeleteDatasetLinkInput!) {
  deleteDatasetLink(input: $input) {
    success
    errors
  }
}
    `;
export type DeleteDatasetLinkMutationFn = Apollo.MutationFunction<DeleteDatasetLinkMutation, DeleteDatasetLinkMutationVariables>;

/**
 * __useDeleteDatasetLinkMutation__
 *
 * To run a mutation, you first call `useDeleteDatasetLinkMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteDatasetLinkMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteDatasetLinkMutation, { data, loading, error }] = useDeleteDatasetLinkMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeleteDatasetLinkMutation(baseOptions?: Apollo.MutationHookOptions<DeleteDatasetLinkMutation, DeleteDatasetLinkMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeleteDatasetLinkMutation, DeleteDatasetLinkMutationVariables>(DeleteDatasetLinkDocument, options);
      }
export type DeleteDatasetLinkMutationHookResult = ReturnType<typeof useDeleteDatasetLinkMutation>;
export type DeleteDatasetLinkMutationResult = Apollo.MutationResult<DeleteDatasetLinkMutation>;
export type DeleteDatasetLinkMutationOptions = Apollo.BaseMutationOptions<DeleteDatasetLinkMutation, DeleteDatasetLinkMutationVariables>;
export const DeleteDatasetDocument = gql`
    mutation DeleteDataset($input: DeleteDatasetInput!) {
  deleteDataset(input: $input) {
    success
    errors
  }
}
    `;
export type DeleteDatasetMutationFn = Apollo.MutationFunction<DeleteDatasetMutation, DeleteDatasetMutationVariables>;

/**
 * __useDeleteDatasetMutation__
 *
 * To run a mutation, you first call `useDeleteDatasetMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteDatasetMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteDatasetMutation, { data, loading, error }] = useDeleteDatasetMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeleteDatasetMutation(baseOptions?: Apollo.MutationHookOptions<DeleteDatasetMutation, DeleteDatasetMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeleteDatasetMutation, DeleteDatasetMutationVariables>(DeleteDatasetDocument, options);
      }
export type DeleteDatasetMutationHookResult = ReturnType<typeof useDeleteDatasetMutation>;
export type DeleteDatasetMutationResult = Apollo.MutationResult<DeleteDatasetMutation>;
export type DeleteDatasetMutationOptions = Apollo.BaseMutationOptions<DeleteDatasetMutation, DeleteDatasetMutationVariables>;