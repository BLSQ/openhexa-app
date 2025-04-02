import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type GetConnectionBySlugQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  connectionSlug: Types.Scalars['String']['input'];
  type: Types.Dhis2MetadataType;
  filters?: Types.InputMaybe<Array<Types.Scalars['String']['input']> | Types.Scalars['String']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type GetConnectionBySlugQuery = { __typename?: 'Query', connectionBySlug?: { __typename?: 'CustomConnection' } | { __typename?: 'DHIS2Connection', queryMetadata: { __typename?: 'DHIS2QueryResultPage', pageNumber: number, totalItems: number, error?: Types.Dhis2ConnectionError | null, items?: Array<{ __typename?: 'DHIS2MetadataItem', id?: string | null, label: string }> | null } } | { __typename?: 'GCSConnection' } | { __typename?: 'IASOConnection' } | { __typename?: 'PostgreSQLConnection' } | { __typename?: 'S3Connection' } | null };


export const GetConnectionBySlugDocument = gql`
    query getConnectionBySlug($workspaceSlug: String!, $connectionSlug: String!, $type: DHIS2MetadataType!, $filters: [String!], $perPage: Int, $page: Int) {
  connectionBySlug(workspaceSlug: $workspaceSlug, connectionSlug: $connectionSlug) {
    ... on DHIS2Connection {
      queryMetadata(type: $type, filters: $filters, perPage: $perPage, page: $page) {
        items {
          id
          label
        }
        pageNumber
        totalItems
        error
      }
    }
  }
}
    `;

/**
 * __useGetConnectionBySlugQuery__
 *
 * To run a query within a React component, call `useGetConnectionBySlugQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetConnectionBySlugQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetConnectionBySlugQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      connectionSlug: // value for 'connectionSlug'
 *      type: // value for 'type'
 *      filters: // value for 'filters'
 *      perPage: // value for 'perPage'
 *      page: // value for 'page'
 *   },
 * });
 */
export function useGetConnectionBySlugQuery(baseOptions: Apollo.QueryHookOptions<GetConnectionBySlugQuery, GetConnectionBySlugQueryVariables> & ({ variables: GetConnectionBySlugQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetConnectionBySlugQuery, GetConnectionBySlugQueryVariables>(GetConnectionBySlugDocument, options);
      }
export function useGetConnectionBySlugLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetConnectionBySlugQuery, GetConnectionBySlugQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetConnectionBySlugQuery, GetConnectionBySlugQueryVariables>(GetConnectionBySlugDocument, options);
        }
export function useGetConnectionBySlugSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetConnectionBySlugQuery, GetConnectionBySlugQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetConnectionBySlugQuery, GetConnectionBySlugQueryVariables>(GetConnectionBySlugDocument, options);
        }
export type GetConnectionBySlugQueryHookResult = ReturnType<typeof useGetConnectionBySlugQuery>;
export type GetConnectionBySlugLazyQueryHookResult = ReturnType<typeof useGetConnectionBySlugLazyQuery>;
export type GetConnectionBySlugSuspenseQueryHookResult = ReturnType<typeof useGetConnectionBySlugSuspenseQuery>;
export type GetConnectionBySlugQueryResult = Apollo.QueryResult<GetConnectionBySlugQuery, GetConnectionBySlugQueryVariables>;