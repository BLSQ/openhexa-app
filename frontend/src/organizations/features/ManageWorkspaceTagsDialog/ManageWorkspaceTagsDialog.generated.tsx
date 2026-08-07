import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { Tag_TagFragmentDoc } from '../../../core/features/Tag.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type SetWorkspaceTagsMutationVariables = Types.Exact<{
  input: Types.SetWorkspaceTagsInput;
}>;


export type SetWorkspaceTagsMutation = { __typename?: 'Mutation', setWorkspaceTags: { __typename?: 'SetWorkspaceTagsResult', success: boolean, errors: Array<Types.SetWorkspaceTagsError>, workspace?: { __typename?: 'Workspace', slug: string, tags: Array<{ __typename?: 'Tag', id: string, name: string }> } | null } };


export const SetWorkspaceTagsDocument = gql`
    mutation SetWorkspaceTags($input: SetWorkspaceTagsInput!) {
  setWorkspaceTags(input: $input) {
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
export type SetWorkspaceTagsMutationFn = Apollo.MutationFunction<SetWorkspaceTagsMutation, SetWorkspaceTagsMutationVariables>;

/**
 * __useSetWorkspaceTagsMutation__
 *
 * To run a mutation, you first call `useSetWorkspaceTagsMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useSetWorkspaceTagsMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [setWorkspaceTagsMutation, { data, loading, error }] = useSetWorkspaceTagsMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useSetWorkspaceTagsMutation(baseOptions?: Apollo.MutationHookOptions<SetWorkspaceTagsMutation, SetWorkspaceTagsMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<SetWorkspaceTagsMutation, SetWorkspaceTagsMutationVariables>(SetWorkspaceTagsDocument, options);
      }
export type SetWorkspaceTagsMutationHookResult = ReturnType<typeof useSetWorkspaceTagsMutation>;
export type SetWorkspaceTagsMutationResult = Apollo.MutationResult<SetWorkspaceTagsMutation>;
export type SetWorkspaceTagsMutationOptions = Apollo.BaseMutationOptions<SetWorkspaceTagsMutation, SetWorkspaceTagsMutationVariables>;