import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type GetFileDownloadUrlMutationVariables = Types.Exact<{
  input: Types.PrepareObjectDownloadInput;
}>;


export type GetFileDownloadUrlMutation = { __typename?: 'Mutation', prepareObjectDownload: { __typename?: 'PrepareObjectDownloadResult', success: boolean, downloadUrl?: any | null } };

export type DeleteBucketObjectMutationVariables = Types.Exact<{
  input: Types.DeleteBucketObjectInput;
}>;


export type DeleteBucketObjectMutation = { __typename?: 'Mutation', deleteBucketObject: { __typename?: 'DeleteBucketObjectResult', success: boolean, errors: Array<Types.DeleteBucketObjectError> } };

export type GetBucketUploadUrlMutationVariables = Types.Exact<{
  input: Types.PrepareObjectUploadInput;
}>;


export type GetBucketUploadUrlMutation = { __typename?: 'Mutation', prepareObjectUpload: { __typename?: 'PrepareObjectUploadResult', success: boolean, uploadUrl?: any | null } };

export type CreateBucketFolderMutationVariables = Types.Exact<{
  input: Types.CreateBucketFolderInput;
}>;


export type CreateBucketFolderMutation = { __typename?: 'Mutation', createBucketFolder: { __typename?: 'CreateBucketFolderResult', success: boolean, errors: Array<Types.CreateBucketFolderError>, folder?: { __typename?: 'BucketObject', key: string, name: string, type: Types.BucketObjectType } | null } };


export const GetFileDownloadUrlDocument = gql`
    mutation GetFileDownloadUrl($input: PrepareObjectDownloadInput!) {
  prepareObjectDownload(input: $input) {
    success
    downloadUrl
  }
}
    `;
export type GetFileDownloadUrlMutationFn = Apollo.MutationFunction<GetFileDownloadUrlMutation, GetFileDownloadUrlMutationVariables>;

/**
 * __useGetFileDownloadUrlMutation__
 *
 * To run a mutation, you first call `useGetFileDownloadUrlMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useGetFileDownloadUrlMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [getFileDownloadUrlMutation, { data, loading, error }] = useGetFileDownloadUrlMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useGetFileDownloadUrlMutation(baseOptions?: Apollo.MutationHookOptions<GetFileDownloadUrlMutation, GetFileDownloadUrlMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<GetFileDownloadUrlMutation, GetFileDownloadUrlMutationVariables>(GetFileDownloadUrlDocument, options);
      }
export type GetFileDownloadUrlMutationHookResult = ReturnType<typeof useGetFileDownloadUrlMutation>;
export type GetFileDownloadUrlMutationResult = Apollo.MutationResult<GetFileDownloadUrlMutation>;
export type GetFileDownloadUrlMutationOptions = Apollo.BaseMutationOptions<GetFileDownloadUrlMutation, GetFileDownloadUrlMutationVariables>;
export const DeleteBucketObjectDocument = gql`
    mutation deleteBucketObject($input: DeleteBucketObjectInput!) {
  deleteBucketObject(input: $input) {
    success
    errors
  }
}
    `;
export type DeleteBucketObjectMutationFn = Apollo.MutationFunction<DeleteBucketObjectMutation, DeleteBucketObjectMutationVariables>;

/**
 * __useDeleteBucketObjectMutation__
 *
 * To run a mutation, you first call `useDeleteBucketObjectMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteBucketObjectMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteBucketObjectMutation, { data, loading, error }] = useDeleteBucketObjectMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeleteBucketObjectMutation(baseOptions?: Apollo.MutationHookOptions<DeleteBucketObjectMutation, DeleteBucketObjectMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeleteBucketObjectMutation, DeleteBucketObjectMutationVariables>(DeleteBucketObjectDocument, options);
      }
export type DeleteBucketObjectMutationHookResult = ReturnType<typeof useDeleteBucketObjectMutation>;
export type DeleteBucketObjectMutationResult = Apollo.MutationResult<DeleteBucketObjectMutation>;
export type DeleteBucketObjectMutationOptions = Apollo.BaseMutationOptions<DeleteBucketObjectMutation, DeleteBucketObjectMutationVariables>;
export const GetBucketUploadUrlDocument = gql`
    mutation GetBucketUploadUrl($input: PrepareObjectUploadInput!) {
  prepareObjectUpload(input: $input) {
    success
    uploadUrl
  }
}
    `;
export type GetBucketUploadUrlMutationFn = Apollo.MutationFunction<GetBucketUploadUrlMutation, GetBucketUploadUrlMutationVariables>;

/**
 * __useGetBucketUploadUrlMutation__
 *
 * To run a mutation, you first call `useGetBucketUploadUrlMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useGetBucketUploadUrlMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [getBucketUploadUrlMutation, { data, loading, error }] = useGetBucketUploadUrlMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useGetBucketUploadUrlMutation(baseOptions?: Apollo.MutationHookOptions<GetBucketUploadUrlMutation, GetBucketUploadUrlMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<GetBucketUploadUrlMutation, GetBucketUploadUrlMutationVariables>(GetBucketUploadUrlDocument, options);
      }
export type GetBucketUploadUrlMutationHookResult = ReturnType<typeof useGetBucketUploadUrlMutation>;
export type GetBucketUploadUrlMutationResult = Apollo.MutationResult<GetBucketUploadUrlMutation>;
export type GetBucketUploadUrlMutationOptions = Apollo.BaseMutationOptions<GetBucketUploadUrlMutation, GetBucketUploadUrlMutationVariables>;
export const CreateBucketFolderDocument = gql`
    mutation CreateBucketFolder($input: CreateBucketFolderInput!) {
  createBucketFolder(input: $input) {
    success
    errors
    folder {
      key
      name
      type
    }
  }
}
    `;
export type CreateBucketFolderMutationFn = Apollo.MutationFunction<CreateBucketFolderMutation, CreateBucketFolderMutationVariables>;

/**
 * __useCreateBucketFolderMutation__
 *
 * To run a mutation, you first call `useCreateBucketFolderMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateBucketFolderMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createBucketFolderMutation, { data, loading, error }] = useCreateBucketFolderMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useCreateBucketFolderMutation(baseOptions?: Apollo.MutationHookOptions<CreateBucketFolderMutation, CreateBucketFolderMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<CreateBucketFolderMutation, CreateBucketFolderMutationVariables>(CreateBucketFolderDocument, options);
      }
export type CreateBucketFolderMutationHookResult = ReturnType<typeof useCreateBucketFolderMutation>;
export type CreateBucketFolderMutationResult = Apollo.MutationResult<CreateBucketFolderMutation>;
export type CreateBucketFolderMutationOptions = Apollo.BaseMutationOptions<CreateBucketFolderMutation, CreateBucketFolderMutationVariables>;