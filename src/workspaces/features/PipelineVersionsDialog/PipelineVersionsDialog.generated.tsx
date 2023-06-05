import * as Types from '../../../graphql-types';

import { gql } from '@apollo/client';
import { User_UserFragmentDoc } from '../../../core/features/User/User.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type PipelineVersionsDialogQueryVariables = Types.Exact<{
  pipelineId: Types.Scalars['UUID']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type PipelineVersionsDialogQuery = { __typename?: 'Query', pipeline?: { __typename?: 'Pipeline', id: string, versions: { __typename?: 'PipelineVersionPage', totalItems: number, items: Array<{ __typename?: 'PipelineVersion', id: string, number: number, user?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null }> } } | null };

export type PipelineVersionsDialog_PipelineFragment = { __typename?: 'Pipeline', id: string, code: string, workspace?: { __typename?: 'Workspace', slug: string } | null, permissions: { __typename?: 'PipelinePermissions', deleteVersion: boolean } };

export const PipelineVersionsDialog_PipelineFragmentDoc = gql`
    fragment PipelineVersionsDialog_pipeline on Pipeline {
  id
  code
  workspace {
    slug
  }
  permissions {
    deleteVersion
  }
}
    `;
export const PipelineVersionsDialogDocument = gql`
    query PipelineVersionsDialog($pipelineId: UUID!, $page: Int, $perPage: Int) {
  pipeline(id: $pipelineId) {
    id
    versions(page: $page, perPage: $perPage) {
      totalItems
      items {
        id
        number
        user {
          ...User_user
        }
      }
    }
  }
}
    ${User_UserFragmentDoc}`;

/**
 * __usePipelineVersionsDialogQuery__
 *
 * To run a query within a React component, call `usePipelineVersionsDialogQuery` and pass it any options that fit your needs.
 * When your component renders, `usePipelineVersionsDialogQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = usePipelineVersionsDialogQuery({
 *   variables: {
 *      pipelineId: // value for 'pipelineId'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function usePipelineVersionsDialogQuery(baseOptions: Apollo.QueryHookOptions<PipelineVersionsDialogQuery, PipelineVersionsDialogQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<PipelineVersionsDialogQuery, PipelineVersionsDialogQueryVariables>(PipelineVersionsDialogDocument, options);
      }
export function usePipelineVersionsDialogLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<PipelineVersionsDialogQuery, PipelineVersionsDialogQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<PipelineVersionsDialogQuery, PipelineVersionsDialogQueryVariables>(PipelineVersionsDialogDocument, options);
        }
export type PipelineVersionsDialogQueryHookResult = ReturnType<typeof usePipelineVersionsDialogQuery>;
export type PipelineVersionsDialogLazyQueryHookResult = ReturnType<typeof usePipelineVersionsDialogLazyQuery>;
export type PipelineVersionsDialogQueryResult = Apollo.QueryResult<PipelineVersionsDialogQuery, PipelineVersionsDialogQueryVariables>;