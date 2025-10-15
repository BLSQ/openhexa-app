import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import { Tag_TagFragmentDoc } from '../../core/features/Tag.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type UpdateWorkspaceTemplateMutationVariables = Types.Exact<{
  input: Types.UpdateTemplateInput;
}>;


export type UpdateWorkspaceTemplateMutation = { __typename?: 'Mutation', updatePipelineTemplate: { __typename?: 'UpdateTemplateResult', success: boolean, errors: Array<Types.UpdateTemplateError>, template?: { __typename?: 'PipelineTemplate', id: string, name: string, description?: string | null, config?: string | null, functionalType?: Types.PipelineFunctionalType | null, tags: Array<{ __typename?: 'Tag', id: string, name: string }> } | null } };

export type DeleteTemplateVersionMutationVariables = Types.Exact<{
  input: Types.DeleteTemplateVersionInput;
}>;


export type DeleteTemplateVersionMutation = { __typename?: 'Mutation', deleteTemplateVersion: { __typename?: 'DeleteTemplateVersionResult', success: boolean, errors: Array<Types.DeleteTemplateVersionError> } };

export type GetTemplateVersionForDownloadQueryVariables = Types.Exact<{
  versionId: Types.Scalars['UUID']['input'];
}>;


export type GetTemplateVersionForDownloadQuery = { __typename?: 'Query', pipelineTemplateVersion?: { __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number, template: { __typename?: 'PipelineTemplate', code: string }, sourcePipelineVersion: { __typename?: 'PipelineVersion', zipfile: string } } | null };


export const UpdateWorkspaceTemplateDocument = gql`
    mutation UpdateWorkspaceTemplate($input: UpdateTemplateInput!) {
  updatePipelineTemplate(input: $input) {
    success
    errors
    template {
      id
      name
      description
      config
      functionalType
      tags {
        ...Tag_tag
      }
    }
  }
}
    ${Tag_TagFragmentDoc}`;
export type UpdateWorkspaceTemplateMutationFn = Apollo.MutationFunction<UpdateWorkspaceTemplateMutation, UpdateWorkspaceTemplateMutationVariables>;

/**
 * __useUpdateWorkspaceTemplateMutation__
 *
 * To run a mutation, you first call `useUpdateWorkspaceTemplateMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateWorkspaceTemplateMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateWorkspaceTemplateMutation, { data, loading, error }] = useUpdateWorkspaceTemplateMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateWorkspaceTemplateMutation(baseOptions?: Apollo.MutationHookOptions<UpdateWorkspaceTemplateMutation, UpdateWorkspaceTemplateMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateWorkspaceTemplateMutation, UpdateWorkspaceTemplateMutationVariables>(UpdateWorkspaceTemplateDocument, options);
      }
export type UpdateWorkspaceTemplateMutationHookResult = ReturnType<typeof useUpdateWorkspaceTemplateMutation>;
export type UpdateWorkspaceTemplateMutationResult = Apollo.MutationResult<UpdateWorkspaceTemplateMutation>;
export type UpdateWorkspaceTemplateMutationOptions = Apollo.BaseMutationOptions<UpdateWorkspaceTemplateMutation, UpdateWorkspaceTemplateMutationVariables>;
export const DeleteTemplateVersionDocument = gql`
    mutation DeleteTemplateVersion($input: DeleteTemplateVersionInput!) {
  deleteTemplateVersion(input: $input) {
    success
    errors
  }
}
    `;
export type DeleteTemplateVersionMutationFn = Apollo.MutationFunction<DeleteTemplateVersionMutation, DeleteTemplateVersionMutationVariables>;

/**
 * __useDeleteTemplateVersionMutation__
 *
 * To run a mutation, you first call `useDeleteTemplateVersionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteTemplateVersionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteTemplateVersionMutation, { data, loading, error }] = useDeleteTemplateVersionMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeleteTemplateVersionMutation(baseOptions?: Apollo.MutationHookOptions<DeleteTemplateVersionMutation, DeleteTemplateVersionMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeleteTemplateVersionMutation, DeleteTemplateVersionMutationVariables>(DeleteTemplateVersionDocument, options);
      }
export type DeleteTemplateVersionMutationHookResult = ReturnType<typeof useDeleteTemplateVersionMutation>;
export type DeleteTemplateVersionMutationResult = Apollo.MutationResult<DeleteTemplateVersionMutation>;
export type DeleteTemplateVersionMutationOptions = Apollo.BaseMutationOptions<DeleteTemplateVersionMutation, DeleteTemplateVersionMutationVariables>;
export const GetTemplateVersionForDownloadDocument = gql`
    query GetTemplateVersionForDownload($versionId: UUID!) {
  pipelineTemplateVersion(id: $versionId) {
    id
    versionNumber
    template {
      code
    }
    sourcePipelineVersion {
      zipfile
    }
  }
}
    `;

/**
 * __useGetTemplateVersionForDownloadQuery__
 *
 * To run a query within a React component, call `useGetTemplateVersionForDownloadQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetTemplateVersionForDownloadQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetTemplateVersionForDownloadQuery({
 *   variables: {
 *      versionId: // value for 'versionId'
 *   },
 * });
 */
export function useGetTemplateVersionForDownloadQuery(baseOptions: Apollo.QueryHookOptions<GetTemplateVersionForDownloadQuery, GetTemplateVersionForDownloadQueryVariables> & ({ variables: GetTemplateVersionForDownloadQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetTemplateVersionForDownloadQuery, GetTemplateVersionForDownloadQueryVariables>(GetTemplateVersionForDownloadDocument, options);
      }
export function useGetTemplateVersionForDownloadLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetTemplateVersionForDownloadQuery, GetTemplateVersionForDownloadQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetTemplateVersionForDownloadQuery, GetTemplateVersionForDownloadQueryVariables>(GetTemplateVersionForDownloadDocument, options);
        }
export function useGetTemplateVersionForDownloadSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetTemplateVersionForDownloadQuery, GetTemplateVersionForDownloadQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetTemplateVersionForDownloadQuery, GetTemplateVersionForDownloadQueryVariables>(GetTemplateVersionForDownloadDocument, options);
        }
export type GetTemplateVersionForDownloadQueryHookResult = ReturnType<typeof useGetTemplateVersionForDownloadQuery>;
export type GetTemplateVersionForDownloadLazyQueryHookResult = ReturnType<typeof useGetTemplateVersionForDownloadLazyQuery>;
export type GetTemplateVersionForDownloadSuspenseQueryHookResult = ReturnType<typeof useGetTemplateVersionForDownloadSuspenseQuery>;
export type GetTemplateVersionForDownloadQueryResult = Apollo.QueryResult<GetTemplateVersionForDownloadQuery, GetTemplateVersionForDownloadQueryVariables>;