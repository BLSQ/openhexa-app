import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type WorkspaceConnectionPickerQueryVariables = Types.Exact<{
  slug: Types.Scalars['String']['input'];
}>;


export type WorkspaceConnectionPickerQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, connections: Array<{ __typename?: 'CustomConnection', id: string, name: string, slug: string, type: Types.ConnectionType } | { __typename?: 'DHIS2Connection', id: string, name: string, slug: string, type: Types.ConnectionType } | { __typename?: 'GCSConnection', id: string, name: string, slug: string, type: Types.ConnectionType } | { __typename?: 'IASOConnection', id: string, name: string, slug: string, type: Types.ConnectionType } | { __typename?: 'PostgreSQLConnection', id: string, name: string, slug: string, type: Types.ConnectionType } | { __typename?: 'S3Connection', id: string, name: string, slug: string, type: Types.ConnectionType }> } | null };

export type WorkspaceConnectionPicker_WorkspaceFragment = { __typename?: 'Workspace', slug: string, connections: Array<{ __typename?: 'CustomConnection', id: string, name: string, slug: string, type: Types.ConnectionType } | { __typename?: 'DHIS2Connection', id: string, name: string, slug: string, type: Types.ConnectionType } | { __typename?: 'GCSConnection', id: string, name: string, slug: string, type: Types.ConnectionType } | { __typename?: 'IASOConnection', id: string, name: string, slug: string, type: Types.ConnectionType } | { __typename?: 'PostgreSQLConnection', id: string, name: string, slug: string, type: Types.ConnectionType } | { __typename?: 'S3Connection', id: string, name: string, slug: string, type: Types.ConnectionType }> };

export const WorkspaceConnectionPicker_WorkspaceFragmentDoc = gql`
    fragment WorkspaceConnectionPicker_workspace on Workspace {
  slug
  connections {
    id
    name
    slug
    type
  }
}
    `;
export const WorkspaceConnectionPickerDocument = gql`
    query WorkspaceConnectionPicker($slug: String!) {
  workspace(slug: $slug) {
    slug
    ...WorkspaceConnectionPicker_workspace
  }
}
    ${WorkspaceConnectionPicker_WorkspaceFragmentDoc}`;

/**
 * __useWorkspaceConnectionPickerQuery__
 *
 * To run a query within a React component, call `useWorkspaceConnectionPickerQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspaceConnectionPickerQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspaceConnectionPickerQuery({
 *   variables: {
 *      slug: // value for 'slug'
 *   },
 * });
 */
export function useWorkspaceConnectionPickerQuery(baseOptions: Apollo.QueryHookOptions<WorkspaceConnectionPickerQuery, WorkspaceConnectionPickerQueryVariables> & ({ variables: WorkspaceConnectionPickerQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspaceConnectionPickerQuery, WorkspaceConnectionPickerQueryVariables>(WorkspaceConnectionPickerDocument, options);
      }
export function useWorkspaceConnectionPickerLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspaceConnectionPickerQuery, WorkspaceConnectionPickerQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspaceConnectionPickerQuery, WorkspaceConnectionPickerQueryVariables>(WorkspaceConnectionPickerDocument, options);
        }
export function useWorkspaceConnectionPickerSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspaceConnectionPickerQuery, WorkspaceConnectionPickerQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspaceConnectionPickerQuery, WorkspaceConnectionPickerQueryVariables>(WorkspaceConnectionPickerDocument, options);
        }
export type WorkspaceConnectionPickerQueryHookResult = ReturnType<typeof useWorkspaceConnectionPickerQuery>;
export type WorkspaceConnectionPickerLazyQueryHookResult = ReturnType<typeof useWorkspaceConnectionPickerLazyQuery>;
export type WorkspaceConnectionPickerSuspenseQueryHookResult = ReturnType<typeof useWorkspaceConnectionPickerSuspenseQuery>;
export type WorkspaceConnectionPickerQueryResult = Apollo.QueryResult<WorkspaceConnectionPickerQuery, WorkspaceConnectionPickerQueryVariables>;