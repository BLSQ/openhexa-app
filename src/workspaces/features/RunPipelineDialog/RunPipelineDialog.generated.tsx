import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { ParameterField_ParameterFragmentDoc } from './ParameterField.generated';
import { PipelineVersionPicker_PipelineFragmentDoc } from '../PipelineVersionPicker/PipelineVersionPicker.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type RunPipelineDialog_VersionFragment = { __typename?: 'PipelineVersion', id: string, versionName: string, createdAt: any, config?: any | null, user?: { __typename?: 'User', displayName: string } | null, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, help?: string | null, type: Types.ParameterType, default?: any | null, required: boolean, choices?: Array<any> | null, multiple: boolean }> };

export type PipelineCurrentVersionQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  pipelineCode: Types.Scalars['String']['input'];
}>;


export type PipelineCurrentVersionQuery = { __typename?: 'Query', pipelineByCode?: { __typename?: 'Pipeline', currentVersion?: { __typename?: 'PipelineVersion', id: string, versionName: string, createdAt: any, config?: any | null, user?: { __typename?: 'User', displayName: string } | null, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, help?: string | null, type: Types.ParameterType, default?: any | null, required: boolean, choices?: Array<any> | null, multiple: boolean }> } | null } | null };

export type RunPipelineDialog_PipelineFragment = { __typename?: 'Pipeline', id: string, code: string, type: Types.PipelineType, workspace: { __typename?: 'Workspace', slug: string }, permissions: { __typename?: 'PipelinePermissions', run: boolean }, currentVersion?: { __typename?: 'PipelineVersion', id: string } | null };

export type RunPipelineDialog_RunFragment = { __typename?: 'PipelineRun', id: string, config: any, version?: { __typename?: 'PipelineVersion', id: string, versionName: string, createdAt: any, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, help?: string | null, type: Types.ParameterType, default?: any | null, required: boolean, choices?: Array<any> | null, multiple: boolean }>, user?: { __typename?: 'User', displayName: string } | null } | null };

export const RunPipelineDialog_VersionFragmentDoc = gql`
    fragment RunPipelineDialog_version on PipelineVersion {
  id
  versionName
  createdAt
  config
  user {
    displayName
  }
  parameters {
    ...ParameterField_parameter
  }
}
    ${ParameterField_ParameterFragmentDoc}`;
export const RunPipelineDialog_PipelineFragmentDoc = gql`
    fragment RunPipelineDialog_pipeline on Pipeline {
  id
  workspace {
    slug
  }
  permissions {
    run
  }
  code
  type
  currentVersion {
    id
  }
  ...PipelineVersionPicker_pipeline
}
    ${PipelineVersionPicker_PipelineFragmentDoc}`;
export const RunPipelineDialog_RunFragmentDoc = gql`
    fragment RunPipelineDialog_run on PipelineRun {
  id
  config
  version {
    id
    versionName
    createdAt
    parameters {
      ...ParameterField_parameter
    }
    user {
      displayName
    }
  }
}
    ${ParameterField_ParameterFragmentDoc}`;
export const PipelineCurrentVersionDocument = gql`
    query PipelineCurrentVersion($workspaceSlug: String!, $pipelineCode: String!) {
  pipelineByCode(workspaceSlug: $workspaceSlug, code: $pipelineCode) {
    currentVersion {
      id
      versionName
      createdAt
      user {
        displayName
      }
      config
      parameters {
        ...ParameterField_parameter
      }
    }
  }
}
    ${ParameterField_ParameterFragmentDoc}`;

/**
 * __usePipelineCurrentVersionQuery__
 *
 * To run a query within a React component, call `usePipelineCurrentVersionQuery` and pass it any options that fit your needs.
 * When your component renders, `usePipelineCurrentVersionQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = usePipelineCurrentVersionQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      pipelineCode: // value for 'pipelineCode'
 *   },
 * });
 */
export function usePipelineCurrentVersionQuery(baseOptions: Apollo.QueryHookOptions<PipelineCurrentVersionQuery, PipelineCurrentVersionQueryVariables> & ({ variables: PipelineCurrentVersionQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<PipelineCurrentVersionQuery, PipelineCurrentVersionQueryVariables>(PipelineCurrentVersionDocument, options);
      }
export function usePipelineCurrentVersionLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<PipelineCurrentVersionQuery, PipelineCurrentVersionQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<PipelineCurrentVersionQuery, PipelineCurrentVersionQueryVariables>(PipelineCurrentVersionDocument, options);
        }
export function usePipelineCurrentVersionSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<PipelineCurrentVersionQuery, PipelineCurrentVersionQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<PipelineCurrentVersionQuery, PipelineCurrentVersionQueryVariables>(PipelineCurrentVersionDocument, options);
        }
export type PipelineCurrentVersionQueryHookResult = ReturnType<typeof usePipelineCurrentVersionQuery>;
export type PipelineCurrentVersionLazyQueryHookResult = ReturnType<typeof usePipelineCurrentVersionLazyQuery>;
export type PipelineCurrentVersionSuspenseQueryHookResult = ReturnType<typeof usePipelineCurrentVersionSuspenseQuery>;
export type PipelineCurrentVersionQueryResult = Apollo.QueryResult<PipelineCurrentVersionQuery, PipelineCurrentVersionQueryVariables>;