import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type GetConnectionBySlugDhis2QueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  connectionSlug: Types.Scalars['String']['input'];
  type: Types.Dhis2MetadataType;
  filters?: Types.InputMaybe<Array<Types.Scalars['String']['input']> | Types.Scalars['String']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type GetConnectionBySlugDhis2Query = { __typename?: 'Query', connectionBySlug?: { __typename?: 'CustomConnection' } | { __typename?: 'DHIS2Connection', queryMetadata: { __typename?: 'DHIS2QueryResultPage', pageNumber: number, totalItems: number, error?: Types.Dhis2ConnectionError | null, items?: Array<{ __typename?: 'DHIS2MetadataItem', id?: string | null, label: string }> | null } } | { __typename?: 'GCSConnection' } | { __typename?: 'IASOConnection' } | { __typename?: 'PostgreSQLConnection' } | { __typename?: 'S3Connection' } | null };


export const GetConnectionBySlugDhis2Document = gql`
    query getConnectionBySlugDhis2($workspaceSlug: String!, $connectionSlug: String!, $type: DHIS2MetadataType!, $filters: [String!], $perPage: Int, $page: Int) {
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
 * __useGetConnectionBySlugDhis2Query__
 *
 * To run a query within a React component, call `useGetConnectionBySlugDhis2Query` and pass it any options that fit your needs.
 * When your component renders, `useGetConnectionBySlugDhis2Query` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetConnectionBySlugDhis2Query({
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
export function useGetConnectionBySlugDhis2Query(baseOptions: Apollo.QueryHookOptions<GetConnectionBySlugDhis2Query, GetConnectionBySlugDhis2QueryVariables> & ({ variables: GetConnectionBySlugDhis2QueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetConnectionBySlugDhis2Query, GetConnectionBySlugDhis2QueryVariables>(GetConnectionBySlugDhis2Document, options);
      }
export function useGetConnectionBySlugDhis2LazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetConnectionBySlugDhis2Query, GetConnectionBySlugDhis2QueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetConnectionBySlugDhis2Query, GetConnectionBySlugDhis2QueryVariables>(GetConnectionBySlugDhis2Document, options);
        }
export function useGetConnectionBySlugDhis2SuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetConnectionBySlugDhis2Query, GetConnectionBySlugDhis2QueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetConnectionBySlugDhis2Query, GetConnectionBySlugDhis2QueryVariables>(GetConnectionBySlugDhis2Document, options);
        }
export type GetConnectionBySlugDhis2QueryHookResult = ReturnType<typeof useGetConnectionBySlugDhis2Query>;
export type GetConnectionBySlugDhis2LazyQueryHookResult = ReturnType<typeof useGetConnectionBySlugDhis2LazyQuery>;
export type GetConnectionBySlugDhis2SuspenseQueryHookResult = ReturnType<typeof useGetConnectionBySlugDhis2SuspenseQuery>;
export type GetConnectionBySlugDhis2QueryResult = Apollo.QueryResult<GetConnectionBySlugDhis2Query, GetConnectionBySlugDhis2QueryVariables>;