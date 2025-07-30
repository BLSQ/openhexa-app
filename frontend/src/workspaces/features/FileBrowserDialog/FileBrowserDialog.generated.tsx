import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type FileBrowserDialogQueryVariables = Types.Exact<{
  slug: Types.Scalars['String']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  prefix?: Types.InputMaybe<Types.Scalars['String']['input']>;
}>;


export type FileBrowserDialogQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, bucket: { __typename?: 'Bucket', objects: { __typename?: 'BucketObjectPage', pageNumber: number, hasNextPage: boolean, items: Array<{ __typename?: 'BucketObject', name: string, key: string, path: string, type: Types.BucketObjectType, updatedAt?: any | null, size?: any | null }> } } } | null };

export type FileBrowserDialog_BucketObjectFragment = { __typename?: 'BucketObject', key: string, name: string, path: string, size?: any | null, updatedAt?: any | null, type: Types.BucketObjectType };

export const FileBrowserDialog_BucketObjectFragmentDoc = gql`
    fragment FileBrowserDialog_bucketObject on BucketObject {
  key
  name
  path
  size
  updatedAt
  type
}
    `;
export const FileBrowserDialogDocument = gql`
    query FileBrowserDialog($slug: String!, $page: Int, $perPage: Int, $prefix: String) {
  workspace(slug: $slug) {
    slug
    bucket {
      objects(page: $page, perPage: $perPage, prefix: $prefix) {
        items {
          name
          key
          path
          type
          updatedAt
          size
          ...FileBrowserDialog_bucketObject
        }
        pageNumber
        hasNextPage
      }
    }
  }
}
    ${FileBrowserDialog_BucketObjectFragmentDoc}`;

/**
 * __useFileBrowserDialogQuery__
 *
 * To run a query within a React component, call `useFileBrowserDialogQuery` and pass it any options that fit your needs.
 * When your component renders, `useFileBrowserDialogQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useFileBrowserDialogQuery({
 *   variables: {
 *      slug: // value for 'slug'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *      prefix: // value for 'prefix'
 *   },
 * });
 */
export function useFileBrowserDialogQuery(baseOptions: Apollo.QueryHookOptions<FileBrowserDialogQuery, FileBrowserDialogQueryVariables> & ({ variables: FileBrowserDialogQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<FileBrowserDialogQuery, FileBrowserDialogQueryVariables>(FileBrowserDialogDocument, options);
      }
export function useFileBrowserDialogLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<FileBrowserDialogQuery, FileBrowserDialogQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<FileBrowserDialogQuery, FileBrowserDialogQueryVariables>(FileBrowserDialogDocument, options);
        }
export function useFileBrowserDialogSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<FileBrowserDialogQuery, FileBrowserDialogQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<FileBrowserDialogQuery, FileBrowserDialogQueryVariables>(FileBrowserDialogDocument, options);
        }
export type FileBrowserDialogQueryHookResult = ReturnType<typeof useFileBrowserDialogQuery>;
export type FileBrowserDialogLazyQueryHookResult = ReturnType<typeof useFileBrowserDialogLazyQuery>;
export type FileBrowserDialogSuspenseQueryHookResult = ReturnType<typeof useFileBrowserDialogSuspenseQuery>;
export type FileBrowserDialogQueryResult = Apollo.QueryResult<FileBrowserDialogQuery, FileBrowserDialogQueryVariables>;