import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type SavedQueryVersion_VersionFragment = { __typename?: 'SavedQueryVersion', id: string, message: string, authorName: string, authorEmail: string, date: any };

export type SavedQueryVersionsQueryVariables = Types.Exact<{
  slug: Types.Scalars['String']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type SavedQueryVersionsQuery = { __typename?: 'Query', savedQueryBySlug?: { __typename?: 'SavedQuery', id: string, versions: { __typename?: 'SavedQueryVersionsPage', page: number, items: Array<{ __typename?: 'SavedQueryVersion', id: string, message: string, authorName: string, authorEmail: string, date: any }> } } | null };

export type SavedQueryCommitDiffQueryVariables = Types.Exact<{
  slug: Types.Scalars['String']['input'];
  ref: Types.Scalars['String']['input'];
}>;


export type SavedQueryCommitDiffQuery = { __typename?: 'Query', savedQueryBySlug?: { __typename?: 'SavedQuery', id: string, commitDiff?: { __typename?: 'SavedQueryCommitDiff', id: string, message: string, authorName: string, authorEmail: string, date: any, rawDiff: string } | null } | null };

export type SavedQueryVersionContentQueryVariables = Types.Exact<{
  slug: Types.Scalars['String']['input'];
  ref: Types.Scalars['String']['input'];
}>;


export type SavedQueryVersionContentQuery = { __typename?: 'Query', savedQueryBySlug?: { __typename?: 'SavedQuery', id: string, versionContent?: string | null } | null };

export const SavedQueryVersion_VersionFragmentDoc = gql`
    fragment SavedQueryVersion_version on SavedQueryVersion {
  id
  message
  authorName
  authorEmail
  date
}
    `;
export const SavedQueryVersionsDocument = gql`
    query SavedQueryVersions($slug: String!, $page: Int, $perPage: Int) {
  savedQueryBySlug(slug: $slug) {
    id
    versions(page: $page, perPage: $perPage) {
      items {
        ...SavedQueryVersion_version
      }
      page
    }
  }
}
    ${SavedQueryVersion_VersionFragmentDoc}`;

/**
 * __useSavedQueryVersionsQuery__
 *
 * To run a query within a React component, call `useSavedQueryVersionsQuery` and pass it any options that fit your needs.
 * When your component renders, `useSavedQueryVersionsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useSavedQueryVersionsQuery({
 *   variables: {
 *      slug: // value for 'slug'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useSavedQueryVersionsQuery(baseOptions: Apollo.QueryHookOptions<SavedQueryVersionsQuery, SavedQueryVersionsQueryVariables> & ({ variables: SavedQueryVersionsQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<SavedQueryVersionsQuery, SavedQueryVersionsQueryVariables>(SavedQueryVersionsDocument, options);
      }
export function useSavedQueryVersionsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<SavedQueryVersionsQuery, SavedQueryVersionsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<SavedQueryVersionsQuery, SavedQueryVersionsQueryVariables>(SavedQueryVersionsDocument, options);
        }
export function useSavedQueryVersionsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<SavedQueryVersionsQuery, SavedQueryVersionsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<SavedQueryVersionsQuery, SavedQueryVersionsQueryVariables>(SavedQueryVersionsDocument, options);
        }
export type SavedQueryVersionsQueryHookResult = ReturnType<typeof useSavedQueryVersionsQuery>;
export type SavedQueryVersionsLazyQueryHookResult = ReturnType<typeof useSavedQueryVersionsLazyQuery>;
export type SavedQueryVersionsSuspenseQueryHookResult = ReturnType<typeof useSavedQueryVersionsSuspenseQuery>;
export type SavedQueryVersionsQueryResult = Apollo.QueryResult<SavedQueryVersionsQuery, SavedQueryVersionsQueryVariables>;
export const SavedQueryCommitDiffDocument = gql`
    query SavedQueryCommitDiff($slug: String!, $ref: String!) {
  savedQueryBySlug(slug: $slug) {
    id
    commitDiff(ref: $ref) {
      id
      message
      authorName
      authorEmail
      date
      rawDiff
    }
  }
}
    `;

/**
 * __useSavedQueryCommitDiffQuery__
 *
 * To run a query within a React component, call `useSavedQueryCommitDiffQuery` and pass it any options that fit your needs.
 * When your component renders, `useSavedQueryCommitDiffQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useSavedQueryCommitDiffQuery({
 *   variables: {
 *      slug: // value for 'slug'
 *      ref: // value for 'ref'
 *   },
 * });
 */
export function useSavedQueryCommitDiffQuery(baseOptions: Apollo.QueryHookOptions<SavedQueryCommitDiffQuery, SavedQueryCommitDiffQueryVariables> & ({ variables: SavedQueryCommitDiffQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<SavedQueryCommitDiffQuery, SavedQueryCommitDiffQueryVariables>(SavedQueryCommitDiffDocument, options);
      }
export function useSavedQueryCommitDiffLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<SavedQueryCommitDiffQuery, SavedQueryCommitDiffQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<SavedQueryCommitDiffQuery, SavedQueryCommitDiffQueryVariables>(SavedQueryCommitDiffDocument, options);
        }
export function useSavedQueryCommitDiffSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<SavedQueryCommitDiffQuery, SavedQueryCommitDiffQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<SavedQueryCommitDiffQuery, SavedQueryCommitDiffQueryVariables>(SavedQueryCommitDiffDocument, options);
        }
export type SavedQueryCommitDiffQueryHookResult = ReturnType<typeof useSavedQueryCommitDiffQuery>;
export type SavedQueryCommitDiffLazyQueryHookResult = ReturnType<typeof useSavedQueryCommitDiffLazyQuery>;
export type SavedQueryCommitDiffSuspenseQueryHookResult = ReturnType<typeof useSavedQueryCommitDiffSuspenseQuery>;
export type SavedQueryCommitDiffQueryResult = Apollo.QueryResult<SavedQueryCommitDiffQuery, SavedQueryCommitDiffQueryVariables>;
export const SavedQueryVersionContentDocument = gql`
    query SavedQueryVersionContent($slug: String!, $ref: String!) {
  savedQueryBySlug(slug: $slug) {
    id
    versionContent(ref: $ref)
  }
}
    `;

/**
 * __useSavedQueryVersionContentQuery__
 *
 * To run a query within a React component, call `useSavedQueryVersionContentQuery` and pass it any options that fit your needs.
 * When your component renders, `useSavedQueryVersionContentQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useSavedQueryVersionContentQuery({
 *   variables: {
 *      slug: // value for 'slug'
 *      ref: // value for 'ref'
 *   },
 * });
 */
export function useSavedQueryVersionContentQuery(baseOptions: Apollo.QueryHookOptions<SavedQueryVersionContentQuery, SavedQueryVersionContentQueryVariables> & ({ variables: SavedQueryVersionContentQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<SavedQueryVersionContentQuery, SavedQueryVersionContentQueryVariables>(SavedQueryVersionContentDocument, options);
      }
export function useSavedQueryVersionContentLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<SavedQueryVersionContentQuery, SavedQueryVersionContentQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<SavedQueryVersionContentQuery, SavedQueryVersionContentQueryVariables>(SavedQueryVersionContentDocument, options);
        }
export function useSavedQueryVersionContentSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<SavedQueryVersionContentQuery, SavedQueryVersionContentQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<SavedQueryVersionContentQuery, SavedQueryVersionContentQueryVariables>(SavedQueryVersionContentDocument, options);
        }
export type SavedQueryVersionContentQueryHookResult = ReturnType<typeof useSavedQueryVersionContentQuery>;
export type SavedQueryVersionContentLazyQueryHookResult = ReturnType<typeof useSavedQueryVersionContentLazyQuery>;
export type SavedQueryVersionContentSuspenseQueryHookResult = ReturnType<typeof useSavedQueryVersionContentSuspenseQuery>;
export type SavedQueryVersionContentQueryResult = Apollo.QueryResult<SavedQueryVersionContentQuery, SavedQueryVersionContentQueryVariables>;