import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { DeletePipelineRecipientTrigger_RecipientFragmentDoc, DeletePipelineRecipientTrigger_PipelineFragmentDoc } from './DeletePipelineRecipientTrigger/DeletePipelineRecipientTrigger.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type PipelineRecipientsQueryVariables = Types.Exact<{
  id: Types.Scalars['UUID']['input'];
}>;


export type PipelineRecipientsQuery = { __typename?: 'Query', pipeline?: { __typename?: 'Pipeline', recipients: Array<{ __typename?: 'PipelineRecipient', id: string, notificationLevel: Types.PipelineNotificationLevel, user: { __typename?: 'User', id: string, displayName: string } }>, workspace: { __typename?: 'Workspace', slug: string, members: { __typename?: 'WorkspaceMembershipPage', totalItems: number } }, permissions: { __typename?: 'PipelinePermissions', update: boolean } } | null };

export type PipelineRecipients_PipelineFragment = { __typename?: 'Pipeline', id: string, code: string, permissions: { __typename?: 'PipelinePermissions', update: boolean } };

export const PipelineRecipients_PipelineFragmentDoc = gql`
    fragment PipelineRecipients_pipeline on Pipeline {
  id
  code
  permissions {
    update
  }
}
    `;
export const PipelineRecipientsDocument = gql`
    query PipelineRecipients($id: UUID!) {
  pipeline(id: $id) {
    recipients {
      id
      user {
        id
        displayName
      }
      notificationLevel
      ...DeletePipelineRecipientTrigger_recipient
    }
    workspace {
      slug
      members {
        totalItems
      }
    }
    ...DeletePipelineRecipientTrigger_pipeline
  }
}
    ${DeletePipelineRecipientTrigger_RecipientFragmentDoc}
${DeletePipelineRecipientTrigger_PipelineFragmentDoc}`;

/**
 * __usePipelineRecipientsQuery__
 *
 * To run a query within a React component, call `usePipelineRecipientsQuery` and pass it any options that fit your needs.
 * When your component renders, `usePipelineRecipientsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = usePipelineRecipientsQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function usePipelineRecipientsQuery(baseOptions: Apollo.QueryHookOptions<PipelineRecipientsQuery, PipelineRecipientsQueryVariables> & ({ variables: PipelineRecipientsQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<PipelineRecipientsQuery, PipelineRecipientsQueryVariables>(PipelineRecipientsDocument, options);
      }
export function usePipelineRecipientsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<PipelineRecipientsQuery, PipelineRecipientsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<PipelineRecipientsQuery, PipelineRecipientsQueryVariables>(PipelineRecipientsDocument, options);
        }
export function usePipelineRecipientsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<PipelineRecipientsQuery, PipelineRecipientsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<PipelineRecipientsQuery, PipelineRecipientsQueryVariables>(PipelineRecipientsDocument, options);
        }
export type PipelineRecipientsQueryHookResult = ReturnType<typeof usePipelineRecipientsQuery>;
export type PipelineRecipientsLazyQueryHookResult = ReturnType<typeof usePipelineRecipientsLazyQuery>;
export type PipelineRecipientsSuspenseQueryHookResult = ReturnType<typeof usePipelineRecipientsSuspenseQuery>;
export type PipelineRecipientsQueryResult = Apollo.QueryResult<PipelineRecipientsQuery, PipelineRecipientsQueryVariables>;