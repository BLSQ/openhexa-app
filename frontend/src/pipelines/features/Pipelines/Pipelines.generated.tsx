import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { PipelineCard_PipelineFragmentDoc } from '../../../workspaces/features/PipelineCard/PipelineCard.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type GetPipelinesQueryVariables = Types.Exact<{
  page: Types.Scalars['Int']['input'];
  perPage: Types.Scalars['Int']['input'];
  name?: Types.InputMaybe<Types.Scalars['String']['input']>;
  workspaceSlug?: Types.InputMaybe<Types.Scalars['String']['input']>;
}>;


export type GetPipelinesQuery = { __typename?: 'Query', pipelines: { __typename?: 'PipelinesPage', pageNumber: number, totalPages: number, totalItems: number, items: Array<{ __typename?: 'Pipeline', id: string, code: string, name?: string | null, schedule?: string | null, description?: string | null, type: Types.PipelineType, currentVersion?: { __typename?: 'PipelineVersion', versionName: string, createdAt: any, user?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null } | null, lastRuns: { __typename?: 'PipelineRunPage', items: Array<{ __typename?: 'PipelineRun', id: string, status: Types.PipelineRunStatus }> } }> } };

export type Pipelines_WorkspaceFragment = { __typename?: 'Workspace', slug: string };

export const Pipelines_WorkspaceFragmentDoc = gql`
    fragment Pipelines_workspace on Workspace {
  slug
}
    `;
export const GetPipelinesDocument = gql`
    query GetPipelines($page: Int!, $perPage: Int!, $name: String, $workspaceSlug: String) {
  pipelines(
    page: $page
    perPage: $perPage
    name: $name
    workspaceSlug: $workspaceSlug
  ) {
    pageNumber
    totalPages
    totalItems
    items {
      ...PipelineCard_pipeline
    }
  }
}
    ${PipelineCard_PipelineFragmentDoc}`;

/**
 * __useGetPipelinesQuery__
 *
 * To run a query within a React component, call `useGetPipelinesQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetPipelinesQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetPipelinesQuery({
 *   variables: {
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *      name: // value for 'name'
 *      workspaceSlug: // value for 'workspaceSlug'
 *   },
 * });
 */
export function useGetPipelinesQuery(baseOptions: Apollo.QueryHookOptions<GetPipelinesQuery, GetPipelinesQueryVariables> & ({ variables: GetPipelinesQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetPipelinesQuery, GetPipelinesQueryVariables>(GetPipelinesDocument, options);
      }
export function useGetPipelinesLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetPipelinesQuery, GetPipelinesQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetPipelinesQuery, GetPipelinesQueryVariables>(GetPipelinesDocument, options);
        }
export function useGetPipelinesSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetPipelinesQuery, GetPipelinesQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetPipelinesQuery, GetPipelinesQueryVariables>(GetPipelinesDocument, options);
        }
export type GetPipelinesQueryHookResult = ReturnType<typeof useGetPipelinesQuery>;
export type GetPipelinesLazyQueryHookResult = ReturnType<typeof useGetPipelinesLazyQuery>;
export type GetPipelinesSuspenseQueryHookResult = ReturnType<typeof useGetPipelinesSuspenseQuery>;
export type GetPipelinesQueryResult = Apollo.QueryResult<GetPipelinesQuery, GetPipelinesQueryVariables>;