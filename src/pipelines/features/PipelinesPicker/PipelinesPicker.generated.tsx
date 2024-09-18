import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type PipelinesPickerQueryVariables = Types.Exact<{ [key: string]: never; }>;


export type PipelinesPickerQuery = { __typename?: 'Query', dags: { __typename?: 'DAGPage', items: Array<{ __typename?: 'DAG', id: string, externalId: string }> } };

export type PipelinesPicker_ValueFragment = { __typename?: 'DAG', id: string, externalId: string };

export const PipelinesPicker_ValueFragmentDoc = gql`
    fragment PipelinesPicker_value on DAG {
  id
  externalId
}
    `;
export const PipelinesPickerDocument = gql`
    query PipelinesPicker {
  dags {
    items {
      ...PipelinesPicker_value
    }
  }
}
    ${PipelinesPicker_ValueFragmentDoc}`;

/**
 * __usePipelinesPickerQuery__
 *
 * To run a query within a React component, call `usePipelinesPickerQuery` and pass it any options that fit your needs.
 * When your component renders, `usePipelinesPickerQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = usePipelinesPickerQuery({
 *   variables: {
 *   },
 * });
 */
export function usePipelinesPickerQuery(baseOptions?: Apollo.QueryHookOptions<PipelinesPickerQuery, PipelinesPickerQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<PipelinesPickerQuery, PipelinesPickerQueryVariables>(PipelinesPickerDocument, options);
      }
export function usePipelinesPickerLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<PipelinesPickerQuery, PipelinesPickerQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<PipelinesPickerQuery, PipelinesPickerQueryVariables>(PipelinesPickerDocument, options);
        }
export function usePipelinesPickerSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<PipelinesPickerQuery, PipelinesPickerQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<PipelinesPickerQuery, PipelinesPickerQueryVariables>(PipelinesPickerDocument, options);
        }
export type PipelinesPickerQueryHookResult = ReturnType<typeof usePipelinesPickerQuery>;
export type PipelinesPickerLazyQueryHookResult = ReturnType<typeof usePipelinesPickerLazyQuery>;
export type PipelinesPickerSuspenseQueryHookResult = ReturnType<typeof usePipelinesPickerSuspenseQuery>;
export type PipelinesPickerQueryResult = Apollo.QueryResult<PipelinesPickerQuery, PipelinesPickerQueryVariables>;