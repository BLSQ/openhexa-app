import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type WorkspaceMemberPickerQueryVariables = Types.Exact<{
  slug: Types.Scalars['String']['input'];
}>;


export type WorkspaceMemberPickerQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, members: { __typename?: 'WorkspaceMembershipPage', items: Array<{ __typename?: 'WorkspaceMembership', id: string, user: { __typename?: 'User', id: string, displayName: string } }> } } | null };

export type WorkspaceMemberPicker_WorkspaceFragment = { __typename?: 'Workspace', slug: string, members: { __typename?: 'WorkspaceMembershipPage', items: Array<{ __typename?: 'WorkspaceMembership', id: string, user: { __typename?: 'User', id: string, displayName: string } }> } };

export const WorkspaceMemberPicker_WorkspaceFragmentDoc = gql`
    fragment WorkspaceMemberPicker_workspace on Workspace {
  slug
  members {
    items {
      id
      user {
        id
        displayName
      }
    }
  }
}
    `;
export const WorkspaceMemberPickerDocument = gql`
    query WorkspaceMemberPicker($slug: String!) {
  workspace(slug: $slug) {
    slug
    ...WorkspaceMemberPicker_workspace
  }
}
    ${WorkspaceMemberPicker_WorkspaceFragmentDoc}`;

/**
 * __useWorkspaceMemberPickerQuery__
 *
 * To run a query within a React component, call `useWorkspaceMemberPickerQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspaceMemberPickerQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspaceMemberPickerQuery({
 *   variables: {
 *      slug: // value for 'slug'
 *   },
 * });
 */
export function useWorkspaceMemberPickerQuery(baseOptions: Apollo.QueryHookOptions<WorkspaceMemberPickerQuery, WorkspaceMemberPickerQueryVariables> & ({ variables: WorkspaceMemberPickerQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspaceMemberPickerQuery, WorkspaceMemberPickerQueryVariables>(WorkspaceMemberPickerDocument, options);
      }
export function useWorkspaceMemberPickerLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspaceMemberPickerQuery, WorkspaceMemberPickerQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspaceMemberPickerQuery, WorkspaceMemberPickerQueryVariables>(WorkspaceMemberPickerDocument, options);
        }
export function useWorkspaceMemberPickerSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspaceMemberPickerQuery, WorkspaceMemberPickerQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspaceMemberPickerQuery, WorkspaceMemberPickerQueryVariables>(WorkspaceMemberPickerDocument, options);
        }
export type WorkspaceMemberPickerQueryHookResult = ReturnType<typeof useWorkspaceMemberPickerQuery>;
export type WorkspaceMemberPickerLazyQueryHookResult = ReturnType<typeof useWorkspaceMemberPickerLazyQuery>;
export type WorkspaceMemberPickerSuspenseQueryHookResult = ReturnType<typeof useWorkspaceMemberPickerSuspenseQuery>;
export type WorkspaceMemberPickerQueryResult = Apollo.QueryResult<WorkspaceMemberPickerQuery, WorkspaceMemberPickerQueryVariables>;