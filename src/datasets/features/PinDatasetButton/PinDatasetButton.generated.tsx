import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type PinDatasetButtonMutationVariables = Types.Exact<{
  input: Types.PinDatasetInput;
}>;


export type PinDatasetButtonMutation = { __typename?: 'Mutation', pinDataset: { __typename?: 'PinDatasetResult', success: boolean, errors: Array<Types.PinDatasetError>, link?: { __typename?: 'DatasetLink', id: string, isPinned: boolean } | null } };

export type PinDatasetButton_LinkFragment = { __typename?: 'DatasetLink', id: string, isPinned: boolean, permissions: { __typename?: 'DatasetLinkPermissions', pin: boolean } };

export const PinDatasetButton_LinkFragmentDoc = gql`
    fragment PinDatasetButton_link on DatasetLink {
  id
  isPinned
  permissions {
    pin
  }
}
    `;
export const PinDatasetButtonDocument = gql`
    mutation PinDatasetButton($input: PinDatasetInput!) {
  pinDataset(input: $input) {
    link {
      id
      isPinned
    }
    success
    errors
  }
}
    `;
export type PinDatasetButtonMutationFn = Apollo.MutationFunction<PinDatasetButtonMutation, PinDatasetButtonMutationVariables>;

/**
 * __usePinDatasetButtonMutation__
 *
 * To run a mutation, you first call `usePinDatasetButtonMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `usePinDatasetButtonMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [pinDatasetButtonMutation, { data, loading, error }] = usePinDatasetButtonMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function usePinDatasetButtonMutation(baseOptions?: Apollo.MutationHookOptions<PinDatasetButtonMutation, PinDatasetButtonMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<PinDatasetButtonMutation, PinDatasetButtonMutationVariables>(PinDatasetButtonDocument, options);
      }
export type PinDatasetButtonMutationHookResult = ReturnType<typeof usePinDatasetButtonMutation>;
export type PinDatasetButtonMutationResult = Apollo.MutationResult<PinDatasetButtonMutation>;
export type PinDatasetButtonMutationOptions = Apollo.BaseMutationOptions<PinDatasetButtonMutation, PinDatasetButtonMutationVariables>;