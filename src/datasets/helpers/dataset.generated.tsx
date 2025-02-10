import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type UpdateDatasetMutationVariables = Types.Exact<{
  input: Types.UpdateDatasetInput;
}>;


export type UpdateDatasetMutation = { __typename?: 'Mutation', updateDataset: { __typename?: 'UpdateDatasetResult', success: boolean, errors: Array<Types.UpdateDatasetError>, dataset?: { __typename?: 'Dataset', id: string, name: string, description?: string | null, updatedAt: any } | null } };

export type UpdateDatasetVersionMutationVariables = Types.Exact<{
  input: Types.UpdateDatasetVersionInput;
}>;


export type UpdateDatasetVersionMutation = { __typename?: 'Mutation', updateDatasetVersion: { __typename?: 'UpdateDatasetVersionResult', success: boolean, errors: Array<Types.UpdateDatasetVersionError>, version?: { __typename?: 'DatasetVersion', id: string, name: string, changelog?: string | null } | null } };

export type CreateDatasetVersionMutationVariables = Types.Exact<{
  input: Types.CreateDatasetVersionInput;
}>;


export type CreateDatasetVersionMutation = { __typename?: 'Mutation', createDatasetVersion: { __typename?: 'CreateDatasetVersionResult', success: boolean, errors: Array<Types.CreateDatasetVersionError>, version?: { __typename?: 'DatasetVersion', id: string, name: string, changelog?: string | null } | null } };

export type GenerateDatasetUploadUrlMutationVariables = Types.Exact<{
  input: Types.GenerateDatasetUploadUrlInput;
}>;


export type GenerateDatasetUploadUrlMutation = { __typename?: 'Mutation', generateDatasetUploadUrl: { __typename?: 'GenerateDatasetUploadUrlResult', success: boolean, errors: Array<Types.CreateDatasetVersionFileError>, uploadUrl?: string | null } };

export type PrepareVersionFileDownloadMutationVariables = Types.Exact<{
  input: Types.PrepareVersionFileDownloadInput;
}>;


export type PrepareVersionFileDownloadMutation = { __typename?: 'Mutation', prepareVersionFileDownload: { __typename?: 'PrepareVersionFileDownloadResult', success: boolean, downloadUrl?: string | null, errors: Array<Types.PrepareVersionFileDownloadError> } };

export type CreateDatasetVersionFileMutationVariables = Types.Exact<{
  input: Types.CreateDatasetVersionFileInput;
}>;


export type CreateDatasetVersionFileMutation = { __typename?: 'Mutation', createDatasetVersionFile: { __typename?: 'CreateDatasetVersionFileResult', success: boolean, errors: Array<Types.CreateDatasetVersionFileError>, file?: { __typename?: 'DatasetVersionFile', id: string, uri: string } | null } };

export type DeleteDatasetLinkMutationVariables = Types.Exact<{
  input: Types.DeleteDatasetLinkInput;
}>;


export type DeleteDatasetLinkMutation = { __typename?: 'Mutation', deleteDatasetLink: { __typename?: 'DeleteDatasetLinkResult', success: boolean, errors: Array<Types.DeleteDatasetLinkError> } };

export type DeleteDatasetMutationVariables = Types.Exact<{
  input: Types.DeleteDatasetInput;
}>;


export type DeleteDatasetMutation = { __typename?: 'Mutation', deleteDataset: { __typename?: 'DeleteDatasetResult', success: boolean, errors: Array<Types.DeleteDatasetError> } };

export type SetMetadataAttributeMutationVariables = Types.Exact<{
  input: Types.SetMetadataAttributeInput;
}>;


export type SetMetadataAttributeMutation = { __typename?: 'Mutation', setMetadataAttribute: { __typename?: 'SetMetadataAttributeResult', success: boolean, errors: Array<Types.SetMetadataAttributeError>, attribute?: { __typename?: 'MetadataAttribute', id: string, key: string, label?: string | null, value?: any | null, system: boolean } | null } };

export type DeleteMetadataAttributeMutationVariables = Types.Exact<{
  input: Types.DeleteMetadataAttributeInput;
}>;


export type DeleteMetadataAttributeMutation = { __typename?: 'Mutation', deleteMetadataAttribute: { __typename?: 'DeleteMetadataAttributeResult', success: boolean, errors: Array<Types.DeleteMetadataAttributeError> } };


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
export const UpdateDatasetVersionDocument = gql`
    mutation UpdateDatasetVersion($input: UpdateDatasetVersionInput!) {
  updateDatasetVersion(input: $input) {
    version {
      id
      name
      changelog
    }
    success
    errors
  }
}
    `;
export type UpdateDatasetVersionMutationFn = Apollo.MutationFunction<UpdateDatasetVersionMutation, UpdateDatasetVersionMutationVariables>;

/**
 * __useUpdateDatasetVersionMutation__
 *
 * To run a mutation, you first call `useUpdateDatasetVersionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateDatasetVersionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateDatasetVersionMutation, { data, loading, error }] = useUpdateDatasetVersionMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateDatasetVersionMutation(baseOptions?: Apollo.MutationHookOptions<UpdateDatasetVersionMutation, UpdateDatasetVersionMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateDatasetVersionMutation, UpdateDatasetVersionMutationVariables>(UpdateDatasetVersionDocument, options);
      }
export type UpdateDatasetVersionMutationHookResult = ReturnType<typeof useUpdateDatasetVersionMutation>;
export type UpdateDatasetVersionMutationResult = Apollo.MutationResult<UpdateDatasetVersionMutation>;
export type UpdateDatasetVersionMutationOptions = Apollo.BaseMutationOptions<UpdateDatasetVersionMutation, UpdateDatasetVersionMutationVariables>;
export const CreateDatasetVersionDocument = gql`
    mutation CreateDatasetVersion($input: CreateDatasetVersionInput!) {
  createDatasetVersion(input: $input) {
    version {
      id
      name
      changelog
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
export const GenerateDatasetUploadUrlDocument = gql`
    mutation generateDatasetUploadUrl($input: GenerateDatasetUploadUrlInput!) {
  generateDatasetUploadUrl(input: $input) {
    success
    errors
    uploadUrl
  }
}
    `;
export type GenerateDatasetUploadUrlMutationFn = Apollo.MutationFunction<GenerateDatasetUploadUrlMutation, GenerateDatasetUploadUrlMutationVariables>;

/**
 * __useGenerateDatasetUploadUrlMutation__
 *
 * To run a mutation, you first call `useGenerateDatasetUploadUrlMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useGenerateDatasetUploadUrlMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [generateDatasetUploadUrlMutation, { data, loading, error }] = useGenerateDatasetUploadUrlMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useGenerateDatasetUploadUrlMutation(baseOptions?: Apollo.MutationHookOptions<GenerateDatasetUploadUrlMutation, GenerateDatasetUploadUrlMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<GenerateDatasetUploadUrlMutation, GenerateDatasetUploadUrlMutationVariables>(GenerateDatasetUploadUrlDocument, options);
      }
export type GenerateDatasetUploadUrlMutationHookResult = ReturnType<typeof useGenerateDatasetUploadUrlMutation>;
export type GenerateDatasetUploadUrlMutationResult = Apollo.MutationResult<GenerateDatasetUploadUrlMutation>;
export type GenerateDatasetUploadUrlMutationOptions = Apollo.BaseMutationOptions<GenerateDatasetUploadUrlMutation, GenerateDatasetUploadUrlMutationVariables>;
export const PrepareVersionFileDownloadDocument = gql`
    mutation PrepareVersionFileDownload($input: PrepareVersionFileDownloadInput!) {
  prepareVersionFileDownload(input: $input) {
    success
    downloadUrl
    errors
  }
}
    `;
export type PrepareVersionFileDownloadMutationFn = Apollo.MutationFunction<PrepareVersionFileDownloadMutation, PrepareVersionFileDownloadMutationVariables>;

/**
 * __usePrepareVersionFileDownloadMutation__
 *
 * To run a mutation, you first call `usePrepareVersionFileDownloadMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `usePrepareVersionFileDownloadMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [prepareVersionFileDownloadMutation, { data, loading, error }] = usePrepareVersionFileDownloadMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function usePrepareVersionFileDownloadMutation(baseOptions?: Apollo.MutationHookOptions<PrepareVersionFileDownloadMutation, PrepareVersionFileDownloadMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<PrepareVersionFileDownloadMutation, PrepareVersionFileDownloadMutationVariables>(PrepareVersionFileDownloadDocument, options);
      }
export type PrepareVersionFileDownloadMutationHookResult = ReturnType<typeof usePrepareVersionFileDownloadMutation>;
export type PrepareVersionFileDownloadMutationResult = Apollo.MutationResult<PrepareVersionFileDownloadMutation>;
export type PrepareVersionFileDownloadMutationOptions = Apollo.BaseMutationOptions<PrepareVersionFileDownloadMutation, PrepareVersionFileDownloadMutationVariables>;
export const CreateDatasetVersionFileDocument = gql`
    mutation CreateDatasetVersionFile($input: CreateDatasetVersionFileInput!) {
  createDatasetVersionFile(input: $input) {
    success
    errors
    file {
      id
      uri
    }
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
export const SetMetadataAttributeDocument = gql`
    mutation SetMetadataAttribute($input: SetMetadataAttributeInput!) {
  setMetadataAttribute(input: $input) {
    success
    errors
    attribute {
      id
      key
      label
      value
      system
    }
  }
}
    `;
export type SetMetadataAttributeMutationFn = Apollo.MutationFunction<SetMetadataAttributeMutation, SetMetadataAttributeMutationVariables>;

/**
 * __useSetMetadataAttributeMutation__
 *
 * To run a mutation, you first call `useSetMetadataAttributeMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useSetMetadataAttributeMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [setMetadataAttributeMutation, { data, loading, error }] = useSetMetadataAttributeMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useSetMetadataAttributeMutation(baseOptions?: Apollo.MutationHookOptions<SetMetadataAttributeMutation, SetMetadataAttributeMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<SetMetadataAttributeMutation, SetMetadataAttributeMutationVariables>(SetMetadataAttributeDocument, options);
      }
export type SetMetadataAttributeMutationHookResult = ReturnType<typeof useSetMetadataAttributeMutation>;
export type SetMetadataAttributeMutationResult = Apollo.MutationResult<SetMetadataAttributeMutation>;
export type SetMetadataAttributeMutationOptions = Apollo.BaseMutationOptions<SetMetadataAttributeMutation, SetMetadataAttributeMutationVariables>;
export const DeleteMetadataAttributeDocument = gql`
    mutation DeleteMetadataAttribute($input: DeleteMetadataAttributeInput!) {
  deleteMetadataAttribute(input: $input) {
    success
    errors
  }
}
    `;
export type DeleteMetadataAttributeMutationFn = Apollo.MutationFunction<DeleteMetadataAttributeMutation, DeleteMetadataAttributeMutationVariables>;

/**
 * __useDeleteMetadataAttributeMutation__
 *
 * To run a mutation, you first call `useDeleteMetadataAttributeMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteMetadataAttributeMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteMetadataAttributeMutation, { data, loading, error }] = useDeleteMetadataAttributeMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeleteMetadataAttributeMutation(baseOptions?: Apollo.MutationHookOptions<DeleteMetadataAttributeMutation, DeleteMetadataAttributeMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeleteMetadataAttributeMutation, DeleteMetadataAttributeMutationVariables>(DeleteMetadataAttributeDocument, options);
      }
export type DeleteMetadataAttributeMutationHookResult = ReturnType<typeof useDeleteMetadataAttributeMutation>;
export type DeleteMetadataAttributeMutationResult = Apollo.MutationResult<DeleteMetadataAttributeMutation>;
export type DeleteMetadataAttributeMutationOptions = Apollo.BaseMutationOptions<DeleteMetadataAttributeMutation, DeleteMetadataAttributeMutationVariables>;