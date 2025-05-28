import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type GetConnectionBySlugIasoQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  connectionSlug: Types.Scalars['String']['input'];
  type: Types.IasoMetadataType;
  search?: Types.InputMaybe<Types.Scalars['String']['input']>;
  filters?: Types.InputMaybe<Array<Types.IasoQueryFilterInput> | Types.IasoQueryFilterInput>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type GetConnectionBySlugIasoQuery = { __typename?: 'Query', connectionBySlug?: { __typename?: 'CustomConnection' } | { __typename?: 'DHIS2Connection' } | { __typename?: 'GCSConnection' } | { __typename?: 'IASOConnection', queryMetadata: { __typename?: 'IASOQueryResultPage', pageNumber: number, totalItems: number, error?: Types.IasoConnectionError | null, items?: Array<{ __typename?: 'IASOMetadataItem', id?: number | null, label: string }> | null } } | { __typename?: 'PostgreSQLConnection' } | { __typename?: 'S3Connection' } | null };


export const GetConnectionBySlugIasoDocument = gql`
    query getConnectionBySlugIaso($workspaceSlug: String!, $connectionSlug: String!, $type: IASOMetadataType!, $search: String, $filters: [IASOQueryFilterInput!], $perPage: Int, $page: Int) {
  connectionBySlug(workspaceSlug: $workspaceSlug, connectionSlug: $connectionSlug) {
    ... on IASOConnection {
      queryMetadata(
        type: $type
        search: $search
        filters: $filters
        perPage: $perPage
        page: $page
      ) {
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
 * __useGetConnectionBySlugIasoQuery__
 *
 * To run a query within a React component, call `useGetConnectionBySlugIasoQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetConnectionBySlugIasoQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetConnectionBySlugIasoQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      connectionSlug: // value for 'connectionSlug'
 *      type: // value for 'type'
 *      search: // value for 'search'
 *      filters: // value for 'filters'
 *      perPage: // value for 'perPage'
 *      page: // value for 'page'
 *   },
 * });
 */
export function useGetConnectionBySlugIasoQuery(baseOptions: Apollo.QueryHookOptions<GetConnectionBySlugIasoQuery, GetConnectionBySlugIasoQueryVariables> & ({ variables: GetConnectionBySlugIasoQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetConnectionBySlugIasoQuery, GetConnectionBySlugIasoQueryVariables>(GetConnectionBySlugIasoDocument, options);
      }
export function useGetConnectionBySlugIasoLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetConnectionBySlugIasoQuery, GetConnectionBySlugIasoQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetConnectionBySlugIasoQuery, GetConnectionBySlugIasoQueryVariables>(GetConnectionBySlugIasoDocument, options);
        }
export function useGetConnectionBySlugIasoSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetConnectionBySlugIasoQuery, GetConnectionBySlugIasoQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetConnectionBySlugIasoQuery, GetConnectionBySlugIasoQueryVariables>(GetConnectionBySlugIasoDocument, options);
        }
export type GetConnectionBySlugIasoQueryHookResult = ReturnType<typeof useGetConnectionBySlugIasoQuery>;
export type GetConnectionBySlugIasoLazyQueryHookResult = ReturnType<typeof useGetConnectionBySlugIasoLazyQuery>;
export type GetConnectionBySlugIasoSuspenseQueryHookResult = ReturnType<typeof useGetConnectionBySlugIasoSuspenseQuery>;
export type GetConnectionBySlugIasoQueryResult = Apollo.QueryResult<GetConnectionBySlugIasoQuery, GetConnectionBySlugIasoQueryVariables>;