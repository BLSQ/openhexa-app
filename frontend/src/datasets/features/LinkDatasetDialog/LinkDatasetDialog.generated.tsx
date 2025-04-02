import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type LinkDatasetDialogMutationVariables = Types.Exact<{
  input: Types.LinkDatasetInput;
}>;


export type LinkDatasetDialogMutation = { __typename?: 'Mutation', linkDataset: { __typename?: 'LinkDatasetResult', success: boolean, errors: Array<Types.LinkDatasetError>, link?: { __typename?: 'DatasetLink', id: string, workspace: { __typename?: 'Workspace', slug: string } } | null } };

export type LinkDatasetDialog_DatasetFragment = { __typename?: 'Dataset', id: string, name: string };

export const LinkDatasetDialog_DatasetFragmentDoc = gql`
    fragment LinkDatasetDialog_dataset on Dataset {
  id
  name
}
    `;
export const LinkDatasetDialogDocument = gql`
    mutation LinkDatasetDialog($input: LinkDatasetInput!) {
  linkDataset(input: $input) {
    success
    errors
    link {
      workspace {
        slug
      }
      id
    }
  }
}
    `;
export type LinkDatasetDialogMutationFn = Apollo.MutationFunction<LinkDatasetDialogMutation, LinkDatasetDialogMutationVariables>;

/**
 * __useLinkDatasetDialogMutation__
 *
 * To run a mutation, you first call `useLinkDatasetDialogMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useLinkDatasetDialogMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [linkDatasetDialogMutation, { data, loading, error }] = useLinkDatasetDialogMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useLinkDatasetDialogMutation(baseOptions?: Apollo.MutationHookOptions<LinkDatasetDialogMutation, LinkDatasetDialogMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<LinkDatasetDialogMutation, LinkDatasetDialogMutationVariables>(LinkDatasetDialogDocument, options);
      }
export type LinkDatasetDialogMutationHookResult = ReturnType<typeof useLinkDatasetDialogMutation>;
export type LinkDatasetDialogMutationResult = Apollo.MutationResult<LinkDatasetDialogMutation>;
export type LinkDatasetDialogMutationOptions = Apollo.BaseMutationOptions<LinkDatasetDialogMutation, LinkDatasetDialogMutationVariables>;