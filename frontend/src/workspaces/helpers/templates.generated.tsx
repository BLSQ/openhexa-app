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

export type GetPipelineVersionForTemplateQueryVariables = Types.Exact<{
  versionId: Types.Scalars['UUID']['input'];
}>;


export type GetPipelineVersionForTemplateQuery = { __typename?: 'Query', pipelineVersion?: { __typename?: 'PipelineVersion', id: string, zipfile: string } | null };


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
export const GetPipelineVersionForTemplateDocument = gql`
    query GetPipelineVersionForTemplate($versionId: UUID!) {
  pipelineVersion(id: $versionId) {
    id
    zipfile
  }
}
    `;

/**
 * __useGetPipelineVersionForTemplateQuery__
 *
 * To run a query within a React component, call `useGetPipelineVersionForTemplateQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetPipelineVersionForTemplateQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetPipelineVersionForTemplateQuery({
 *   variables: {
 *      versionId: // value for 'versionId'
 *   },
 * });
 */
export function useGetPipelineVersionForTemplateQuery(baseOptions: Apollo.QueryHookOptions<GetPipelineVersionForTemplateQuery, GetPipelineVersionForTemplateQueryVariables> & ({ variables: GetPipelineVersionForTemplateQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetPipelineVersionForTemplateQuery, GetPipelineVersionForTemplateQueryVariables>(GetPipelineVersionForTemplateDocument, options);
      }
export function useGetPipelineVersionForTemplateLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetPipelineVersionForTemplateQuery, GetPipelineVersionForTemplateQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetPipelineVersionForTemplateQuery, GetPipelineVersionForTemplateQueryVariables>(GetPipelineVersionForTemplateDocument, options);
        }
export function useGetPipelineVersionForTemplateSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetPipelineVersionForTemplateQuery, GetPipelineVersionForTemplateQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetPipelineVersionForTemplateQuery, GetPipelineVersionForTemplateQueryVariables>(GetPipelineVersionForTemplateDocument, options);
        }
export type GetPipelineVersionForTemplateQueryHookResult = ReturnType<typeof useGetPipelineVersionForTemplateQuery>;
export type GetPipelineVersionForTemplateLazyQueryHookResult = ReturnType<typeof useGetPipelineVersionForTemplateLazyQuery>;
export type GetPipelineVersionForTemplateSuspenseQueryHookResult = ReturnType<typeof useGetPipelineVersionForTemplateSuspenseQuery>;
export type GetPipelineVersionForTemplateQueryResult = Apollo.QueryResult<GetPipelineVersionForTemplateQuery, GetPipelineVersionForTemplateQueryVariables>;