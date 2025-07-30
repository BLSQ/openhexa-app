import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type FileBrowserModalQueryVariables = Types.Exact<{
  slug: Types.Scalars['String']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  prefix?: Types.InputMaybe<Types.Scalars['String']['input']>;
}>;


export type FileBrowserModalQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, bucket: { __typename?: 'Bucket', objects: { __typename?: 'BucketObjectPage', pageNumber: number, hasNextPage: boolean, items: Array<{ __typename?: 'BucketObject', name: string, key: string, path: string, type: Types.BucketObjectType, updatedAt?: any | null, size?: any | null }> } } } | null };

export type FileBrowserModal_BucketObjectFragment = { __typename?: 'BucketObject', key: string, name: string, path: string, size?: any | null, updatedAt?: any | null, type: Types.BucketObjectType };

export const FileBrowserModal_BucketObjectFragmentDoc = gql`
    fragment FileBrowserModal_bucketObject on BucketObject {
  key
  name
  path
  size
  updatedAt
  type
}
    `;
export const FileBrowserModalDocument = gql`
    query FileBrowserModal($slug: String!, $page: Int, $perPage: Int, $prefix: String) {
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
          ...FileBrowserModal_bucketObject
        }
        pageNumber
        hasNextPage
      }
    }
  }
}
    ${FileBrowserModal_BucketObjectFragmentDoc}`;

/**
 * __useFileBrowserModalQuery__
 *
 * To run a query within a React component, call `useFileBrowserModalQuery` and pass it any options that fit your needs.
 * When your component renders, `useFileBrowserModalQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useFileBrowserModalQuery({
 *   variables: {
 *      slug: // value for 'slug'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *      prefix: // value for 'prefix'
 *   },
 * });
 */
export function useFileBrowserModalQuery(baseOptions: Apollo.QueryHookOptions<FileBrowserModalQuery, FileBrowserModalQueryVariables> & ({ variables: FileBrowserModalQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<FileBrowserModalQuery, FileBrowserModalQueryVariables>(FileBrowserModalDocument, options);
      }
export function useFileBrowserModalLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<FileBrowserModalQuery, FileBrowserModalQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<FileBrowserModalQuery, FileBrowserModalQueryVariables>(FileBrowserModalDocument, options);
        }
export function useFileBrowserModalSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<FileBrowserModalQuery, FileBrowserModalQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<FileBrowserModalQuery, FileBrowserModalQueryVariables>(FileBrowserModalDocument, options);
        }
export type FileBrowserModalQueryHookResult = ReturnType<typeof useFileBrowserModalQuery>;
export type FileBrowserModalLazyQueryHookResult = ReturnType<typeof useFileBrowserModalLazyQuery>;
export type FileBrowserModalSuspenseQueryHookResult = ReturnType<typeof useFileBrowserModalSuspenseQuery>;
export type FileBrowserModalQueryResult = Apollo.QueryResult<FileBrowserModalQuery, FileBrowserModalQueryVariables>;