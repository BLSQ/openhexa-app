import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type DownloadVersionFileMutationVariables = Types.Exact<{
  input: Types.PrepareVersionFileDownloadInput;
}>;


export type DownloadVersionFileMutation = { __typename?: 'Mutation', prepareVersionFileDownload: { __typename?: 'PrepareVersionFileDownloadResult', success: boolean, downloadUrl?: string | null, errors: Array<Types.PrepareVersionFileDownloadError> } };

export type DownloadVersionFile_FileFragment = { __typename?: 'DatasetVersionFile', id: string, filename: string };

export const DownloadVersionFile_FileFragmentDoc = gql`
    fragment DownloadVersionFile_file on DatasetVersionFile {
  id
  filename
}
    `;
export const DownloadVersionFileDocument = gql`
    mutation DownloadVersionFile($input: PrepareVersionFileDownloadInput!) {
  prepareVersionFileDownload(input: $input) {
    success
    downloadUrl
    errors
  }
}
    `;
export type DownloadVersionFileMutationFn = Apollo.MutationFunction<DownloadVersionFileMutation, DownloadVersionFileMutationVariables>;

/**
 * __useDownloadVersionFileMutation__
 *
 * To run a mutation, you first call `useDownloadVersionFileMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDownloadVersionFileMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [downloadVersionFileMutation, { data, loading, error }] = useDownloadVersionFileMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDownloadVersionFileMutation(baseOptions?: Apollo.MutationHookOptions<DownloadVersionFileMutation, DownloadVersionFileMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DownloadVersionFileMutation, DownloadVersionFileMutationVariables>(DownloadVersionFileDocument, options);
      }
export type DownloadVersionFileMutationHookResult = ReturnType<typeof useDownloadVersionFileMutation>;
export type DownloadVersionFileMutationResult = Apollo.MutationResult<DownloadVersionFileMutation>;
export type DownloadVersionFileMutationOptions = Apollo.BaseMutationOptions<DownloadVersionFileMutation, DownloadVersionFileMutationVariables>;