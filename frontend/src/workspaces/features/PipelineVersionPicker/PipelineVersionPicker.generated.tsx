import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type PipelineVersionPickerQueryVariables = Types.Exact<{
  pipelineId: Types.Scalars['UUID']['input'];
}>;


export type PipelineVersionPickerQuery = { __typename?: 'Query', pipeline?: { __typename?: 'Pipeline', versions: { __typename?: 'PipelineVersionPage', items: Array<{ __typename?: 'PipelineVersion', id: string, versionName: string, createdAt: any, config?: any | null, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, help?: string | null, type: Types.ParameterType, default?: any | null, required: boolean, choices?: Array<any> | null, multiple: boolean }>, user?: { __typename?: 'User', displayName: string } | null }> } } | null };

export type PipelineVersionPicker_PipelineFragment = { __typename?: 'Pipeline', id: string };

export type PipelineVersionPicker_VersionFragment = { __typename?: 'PipelineVersion', id: string, versionName: string, createdAt: any, config?: any | null, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, help?: string | null, type: Types.ParameterType, default?: any | null, required: boolean, choices?: Array<any> | null, multiple: boolean }>, user?: { __typename?: 'User', displayName: string } | null };

export const PipelineVersionPicker_PipelineFragmentDoc = gql`
    fragment PipelineVersionPicker_pipeline on Pipeline {
  id
}
    `;
export const PipelineVersionPicker_VersionFragmentDoc = gql`
    fragment PipelineVersionPicker_version on PipelineVersion {
  id
  versionName
  createdAt
  config
  parameters {
    code
    name
    help
    type
    default
    required
    choices
    multiple
  }
  user {
    displayName
  }
}
    `;
export const PipelineVersionPickerDocument = gql`
    query PipelineVersionPicker($pipelineId: UUID!) {
  pipeline(id: $pipelineId) {
    versions {
      items {
        ...PipelineVersionPicker_version
      }
    }
  }
}
    ${PipelineVersionPicker_VersionFragmentDoc}`;

/**
 * __usePipelineVersionPickerQuery__
 *
 * To run a query within a React component, call `usePipelineVersionPickerQuery` and pass it any options that fit your needs.
 * When your component renders, `usePipelineVersionPickerQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = usePipelineVersionPickerQuery({
 *   variables: {
 *      pipelineId: // value for 'pipelineId'
 *   },
 * });
 */
export function usePipelineVersionPickerQuery(baseOptions: Apollo.QueryHookOptions<PipelineVersionPickerQuery, PipelineVersionPickerQueryVariables> & ({ variables: PipelineVersionPickerQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<PipelineVersionPickerQuery, PipelineVersionPickerQueryVariables>(PipelineVersionPickerDocument, options);
      }
export function usePipelineVersionPickerLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<PipelineVersionPickerQuery, PipelineVersionPickerQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<PipelineVersionPickerQuery, PipelineVersionPickerQueryVariables>(PipelineVersionPickerDocument, options);
        }
export function usePipelineVersionPickerSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<PipelineVersionPickerQuery, PipelineVersionPickerQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<PipelineVersionPickerQuery, PipelineVersionPickerQueryVariables>(PipelineVersionPickerDocument, options);
        }
export type PipelineVersionPickerQueryHookResult = ReturnType<typeof usePipelineVersionPickerQuery>;
export type PipelineVersionPickerLazyQueryHookResult = ReturnType<typeof usePipelineVersionPickerLazyQuery>;
export type PipelineVersionPickerSuspenseQueryHookResult = ReturnType<typeof usePipelineVersionPickerSuspenseQuery>;
export type PipelineVersionPickerQueryResult = Apollo.QueryResult<PipelineVersionPickerQuery, PipelineVersionPickerQueryVariables>;