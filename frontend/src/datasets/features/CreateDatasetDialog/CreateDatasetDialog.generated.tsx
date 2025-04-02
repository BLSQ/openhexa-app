import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type CreateDatasetDialogMutationVariables = Types.Exact<{
  input: Types.CreateDatasetInput;
}>;


export type CreateDatasetDialogMutation = { __typename?: 'Mutation', createDataset: { __typename?: 'CreateDatasetResult', success: boolean, errors: Array<Types.CreateDatasetError>, dataset?: { __typename?: 'Dataset', id: string, slug: string } | null, link?: { __typename?: 'DatasetLink', id: string } | null } };

export type CreateDatasetDialog_WorkspaceFragment = { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', createDataset: boolean } };

export const CreateDatasetDialog_WorkspaceFragmentDoc = gql`
    fragment CreateDatasetDialog_workspace on Workspace {
  slug
  name
  permissions {
    createDataset
  }
}
    `;
export const CreateDatasetDialogDocument = gql`
    mutation CreateDatasetDialog($input: CreateDatasetInput!) {
  createDataset(input: $input) {
    dataset {
      id
      slug
    }
    link {
      id
    }
    success
    errors
  }
}
    `;
export type CreateDatasetDialogMutationFn = Apollo.MutationFunction<CreateDatasetDialogMutation, CreateDatasetDialogMutationVariables>;

/**
 * __useCreateDatasetDialogMutation__
 *
 * To run a mutation, you first call `useCreateDatasetDialogMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateDatasetDialogMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createDatasetDialogMutation, { data, loading, error }] = useCreateDatasetDialogMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useCreateDatasetDialogMutation(baseOptions?: Apollo.MutationHookOptions<CreateDatasetDialogMutation, CreateDatasetDialogMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<CreateDatasetDialogMutation, CreateDatasetDialogMutationVariables>(CreateDatasetDialogDocument, options);
      }
export type CreateDatasetDialogMutationHookResult = ReturnType<typeof useCreateDatasetDialogMutation>;
export type CreateDatasetDialogMutationResult = Apollo.MutationResult<CreateDatasetDialogMutation>;
export type CreateDatasetDialogMutationOptions = Apollo.BaseMutationOptions<CreateDatasetDialogMutation, CreateDatasetDialogMutationVariables>;