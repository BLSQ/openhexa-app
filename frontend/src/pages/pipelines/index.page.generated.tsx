import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import { CountryBadge_CountryFragmentDoc } from '../../core/features/CountryBadge.generated';
import { Tag_TagFragmentDoc } from '../../core/features/Tag.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type PipelinesPageQueryVariables = Types.Exact<{
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type PipelinesPageQuery = { __typename?: 'Query', dags: { __typename?: 'DAGPage', totalPages: number, totalItems: number, items: Array<{ __typename?: 'DAG', label: string, id: string, externalId: string, countries: Array<{ __typename?: 'Country', code: string, name: string }>, tags: Array<{ __typename?: 'Tag', id: string, name: string }>, runs: { __typename?: 'DAGRunPage', items: Array<{ __typename?: 'DAGRun', id: string, status: Types.DagRunStatus, executionDate?: any | null }> } }> } };


export const PipelinesPageDocument = gql`
    query PipelinesPage($page: Int, $perPage: Int = 15) {
  dags(page: $page, perPage: $perPage) {
    totalPages
    totalItems
    items {
      label
      countries {
        ...CountryBadge_country
      }
      tags {
        ...Tag_tag
      }
      id
      externalId
      runs(orderBy: EXECUTION_DATE_DESC, perPage: 1) {
        items {
          id
          status
          executionDate
        }
      }
    }
  }
}
    ${CountryBadge_CountryFragmentDoc}
${Tag_TagFragmentDoc}`;

/**
 * __usePipelinesPageQuery__
 *
 * To run a query within a React component, call `usePipelinesPageQuery` and pass it any options that fit your needs.
 * When your component renders, `usePipelinesPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = usePipelinesPageQuery({
 *   variables: {
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function usePipelinesPageQuery(baseOptions?: Apollo.QueryHookOptions<PipelinesPageQuery, PipelinesPageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<PipelinesPageQuery, PipelinesPageQueryVariables>(PipelinesPageDocument, options);
      }
export function usePipelinesPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<PipelinesPageQuery, PipelinesPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<PipelinesPageQuery, PipelinesPageQueryVariables>(PipelinesPageDocument, options);
        }
export function usePipelinesPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<PipelinesPageQuery, PipelinesPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<PipelinesPageQuery, PipelinesPageQueryVariables>(PipelinesPageDocument, options);
        }
export type PipelinesPageQueryHookResult = ReturnType<typeof usePipelinesPageQuery>;
export type PipelinesPageLazyQueryHookResult = ReturnType<typeof usePipelinesPageLazyQuery>;
export type PipelinesPageSuspenseQueryHookResult = ReturnType<typeof usePipelinesPageSuspenseQuery>;
export type PipelinesPageQueryResult = Apollo.QueryResult<PipelinesPageQuery, PipelinesPageQueryVariables>;