import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { Tag_TagFragmentDoc } from '../../../core/features/Tag.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type UpdateWorkspaceTagsMutationVariables = Types.Exact<{
  input: Types.UpdateWorkspaceInput;
}>;


export type UpdateWorkspaceTagsMutation = { __typename?: 'Mutation', updateWorkspace: { __typename?: 'UpdateWorkspaceResult', success: boolean, errors: Array<Types.UpdateWorkspaceError>, workspace?: { __typename?: 'Workspace', slug: string, tags: Array<{ __typename?: 'Tag', id: string, name: string }> } | null } };


export const UpdateWorkspaceTagsDocument = gql`
    mutation UpdateWorkspaceTags($input: UpdateWorkspaceInput!) {
  updateWorkspace(input: $input) {
    success
    errors
    workspace {
      slug
      tags {
        ...Tag_tag
      }
    }
  }
}
    ${Tag_TagFragmentDoc}`;
export type UpdateWorkspaceTagsMutationFn = Apollo.MutationFunction<UpdateWorkspaceTagsMutation, UpdateWorkspaceTagsMutationVariables>;

/**
 * __useUpdateWorkspaceTagsMutation__
 *
 * To run a mutation, you first call `useUpdateWorkspaceTagsMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateWorkspaceTagsMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateWorkspaceTagsMutation, { data, loading, error }] = useUpdateWorkspaceTagsMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateWorkspaceTagsMutation(baseOptions?: Apollo.MutationHookOptions<UpdateWorkspaceTagsMutation, UpdateWorkspaceTagsMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateWorkspaceTagsMutation, UpdateWorkspaceTagsMutationVariables>(UpdateWorkspaceTagsDocument, options);
      }
export type UpdateWorkspaceTagsMutationHookResult = ReturnType<typeof useUpdateWorkspaceTagsMutation>;
export type UpdateWorkspaceTagsMutationResult = Apollo.MutationResult<UpdateWorkspaceTagsMutation>;
export type UpdateWorkspaceTagsMutationOptions = Apollo.BaseMutationOptions<UpdateWorkspaceTagsMutation, UpdateWorkspaceTagsMutationVariables>;