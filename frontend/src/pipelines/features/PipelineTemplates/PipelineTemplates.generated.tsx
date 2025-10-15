import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { User_UserFragmentDoc } from '../../../core/features/User/User.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type GetPipelineTemplatesQueryVariables = Types.Exact<{
  page: Types.Scalars['Int']['input'];
  perPage: Types.Scalars['Int']['input'];
  search?: Types.InputMaybe<Types.Scalars['String']['input']>;
  currentWorkspaceSlug: Types.Scalars['String']['input'];
  workspaceSlug?: Types.InputMaybe<Types.Scalars['String']['input']>;
  tags?: Types.InputMaybe<Array<Types.Scalars['String']['input']> | Types.Scalars['String']['input']>;
  functionalType?: Types.InputMaybe<Types.PipelineFunctionalType>;
  organizationName?: Types.InputMaybe<Types.Scalars['String']['input']>;
}>;


export type GetPipelineTemplatesQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, pipelineTemplateTags: Array<string> } | null, pipelineTemplates: { __typename?: 'PipelineTemplatePage', pageNumber: number, totalPages: number, totalItems: number, items: Array<{ __typename?: 'PipelineTemplate', id: string, description?: string | null, code: string, name: string, functionalType?: Types.PipelineFunctionalType | null, tags: Array<{ __typename?: 'Tag', id: string, name: string }>, permissions: { __typename?: 'PipelineTemplatePermissions', delete: boolean }, workspace?: { __typename?: 'Workspace', slug: string, name: string, organization?: { __typename?: 'Organization', id: string, name: string, logo?: string | null } | null } | null, currentVersion?: { __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number, createdAt: any, user?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null, template: { __typename?: 'PipelineTemplate', sourcePipeline?: { __typename?: 'Pipeline', name?: string | null } | null } } | null }> } };

export type PipelineTemplates_WorkspaceFragment = { __typename?: 'Workspace', slug: string };

export const PipelineTemplates_WorkspaceFragmentDoc = gql`
    fragment PipelineTemplates_workspace on Workspace {
  slug
}
    `;
export const GetPipelineTemplatesDocument = gql`
    query GetPipelineTemplates($page: Int!, $perPage: Int!, $search: String, $currentWorkspaceSlug: String!, $workspaceSlug: String, $tags: [String!], $functionalType: PipelineFunctionalType, $organizationName: String) {
  workspace(slug: $currentWorkspaceSlug) {
    slug
    pipelineTemplateTags
  }
  pipelineTemplates(
    page: $page
    perPage: $perPage
    search: $search
    workspaceSlug: $workspaceSlug
    tags: $tags
    functionalType: $functionalType
    organizationName: $organizationName
  ) {
    pageNumber
    totalPages
    totalItems
    items {
      id
      description
      code
      name
      functionalType
      tags {
        id
        name
      }
      permissions {
        delete
      }
      workspace {
        slug
        name
        organization {
          id
          name
          logo
        }
      }
      currentVersion {
        id
        versionNumber
        createdAt
        user {
          ...User_user
        }
        template {
          sourcePipeline {
            name
          }
        }
      }
    }
  }
}
    ${User_UserFragmentDoc}`;

/**
 * __useGetPipelineTemplatesQuery__
 *
 * To run a query within a React component, call `useGetPipelineTemplatesQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetPipelineTemplatesQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetPipelineTemplatesQuery({
 *   variables: {
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *      search: // value for 'search'
 *      currentWorkspaceSlug: // value for 'currentWorkspaceSlug'
 *      workspaceSlug: // value for 'workspaceSlug'
 *      tags: // value for 'tags'
 *      functionalType: // value for 'functionalType'
 *      organizationName: // value for 'organizationName'
 *   },
 * });
 */
export function useGetPipelineTemplatesQuery(baseOptions: Apollo.QueryHookOptions<GetPipelineTemplatesQuery, GetPipelineTemplatesQueryVariables> & ({ variables: GetPipelineTemplatesQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetPipelineTemplatesQuery, GetPipelineTemplatesQueryVariables>(GetPipelineTemplatesDocument, options);
      }
export function useGetPipelineTemplatesLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetPipelineTemplatesQuery, GetPipelineTemplatesQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetPipelineTemplatesQuery, GetPipelineTemplatesQueryVariables>(GetPipelineTemplatesDocument, options);
        }
export function useGetPipelineTemplatesSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetPipelineTemplatesQuery, GetPipelineTemplatesQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetPipelineTemplatesQuery, GetPipelineTemplatesQueryVariables>(GetPipelineTemplatesDocument, options);
        }
export type GetPipelineTemplatesQueryHookResult = ReturnType<typeof useGetPipelineTemplatesQuery>;
export type GetPipelineTemplatesLazyQueryHookResult = ReturnType<typeof useGetPipelineTemplatesLazyQuery>;
export type GetPipelineTemplatesSuspenseQueryHookResult = ReturnType<typeof useGetPipelineTemplatesSuspenseQuery>;
export type GetPipelineTemplatesQueryResult = Apollo.QueryResult<GetPipelineTemplatesQuery, GetPipelineTemplatesQueryVariables>;