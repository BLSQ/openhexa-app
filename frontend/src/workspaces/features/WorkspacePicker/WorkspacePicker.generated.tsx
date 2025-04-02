import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type WorkspacePickerQueryVariables = Types.Exact<{
  query?: Types.InputMaybe<Types.Scalars['String']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type WorkspacePickerQuery = { __typename?: 'Query', workspaces: { __typename?: 'WorkspacePage', totalItems: number, items: Array<{ __typename?: 'Workspace', slug: string, name: string }> } };

export type WorkspacePicker_ValueFragment = { __typename?: 'Workspace', slug: string, name: string };

export const WorkspacePicker_ValueFragmentDoc = gql`
    fragment WorkspacePicker_value on Workspace {
  slug
  name
}
    `;
export const WorkspacePickerDocument = gql`
    query WorkspacePicker($query: String, $perPage: Int = 10) {
  workspaces(query: $query, page: 1, perPage: $perPage) {
    totalItems
    items {
      ...WorkspacePicker_value
    }
  }
}
    ${WorkspacePicker_ValueFragmentDoc}`;

/**
 * __useWorkspacePickerQuery__
 *
 * To run a query within a React component, call `useWorkspacePickerQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspacePickerQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspacePickerQuery({
 *   variables: {
 *      query: // value for 'query'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useWorkspacePickerQuery(baseOptions?: Apollo.QueryHookOptions<WorkspacePickerQuery, WorkspacePickerQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspacePickerQuery, WorkspacePickerQueryVariables>(WorkspacePickerDocument, options);
      }
export function useWorkspacePickerLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspacePickerQuery, WorkspacePickerQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspacePickerQuery, WorkspacePickerQueryVariables>(WorkspacePickerDocument, options);
        }
export function useWorkspacePickerSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspacePickerQuery, WorkspacePickerQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspacePickerQuery, WorkspacePickerQueryVariables>(WorkspacePickerDocument, options);
        }
export type WorkspacePickerQueryHookResult = ReturnType<typeof useWorkspacePickerQuery>;
export type WorkspacePickerLazyQueryHookResult = ReturnType<typeof useWorkspacePickerLazyQuery>;
export type WorkspacePickerSuspenseQueryHookResult = ReturnType<typeof useWorkspacePickerSuspenseQuery>;
export type WorkspacePickerQueryResult = Apollo.QueryResult<WorkspacePickerQuery, WorkspacePickerQueryVariables>;