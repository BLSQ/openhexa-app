import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type AssistantModelsQueryVariables = Types.Exact<{ [key: string]: never; }>;


export type AssistantModelsQuery = { __typename?: 'Query', assistantModels: Array<{ __typename?: 'AssistantModelConfig', id: string, label: string }> };


export const AssistantModelsDocument = gql`
    query AssistantModels {
  assistantModels {
    id
    label
  }
}
    `;

/**
 * __useAssistantModelsQuery__
 *
 * To run a query within a React component, call `useAssistantModelsQuery` and pass it any options that fit your needs.
 * When your component renders, `useAssistantModelsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAssistantModelsQuery({
 *   variables: {
 *   },
 * });
 */
export function useAssistantModelsQuery(baseOptions?: Apollo.QueryHookOptions<AssistantModelsQuery, AssistantModelsQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<AssistantModelsQuery, AssistantModelsQueryVariables>(AssistantModelsDocument, options);
      }
export function useAssistantModelsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<AssistantModelsQuery, AssistantModelsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<AssistantModelsQuery, AssistantModelsQueryVariables>(AssistantModelsDocument, options);
        }
export function useAssistantModelsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<AssistantModelsQuery, AssistantModelsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<AssistantModelsQuery, AssistantModelsQueryVariables>(AssistantModelsDocument, options);
        }
export type AssistantModelsQueryHookResult = ReturnType<typeof useAssistantModelsQuery>;
export type AssistantModelsLazyQueryHookResult = ReturnType<typeof useAssistantModelsLazyQuery>;
export type AssistantModelsSuspenseQueryHookResult = ReturnType<typeof useAssistantModelsSuspenseQuery>;
export type AssistantModelsQueryResult = Apollo.QueryResult<AssistantModelsQuery, AssistantModelsQueryVariables>;