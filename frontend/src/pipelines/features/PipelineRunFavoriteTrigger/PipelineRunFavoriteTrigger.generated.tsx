import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { PipelineRunFavoriteIcon_RunFragmentDoc } from '../PipelineRunFavoriteIcon/PipelineRunFavoriteIcon.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type SetFavoriteRunMutationVariables = Types.Exact<{
  input: Types.SetDagRunFavoriteInput;
}>;


export type SetFavoriteRunMutation = { __typename?: 'Mutation', setDAGRunFavorite?: { __typename?: 'SetDAGRunFavoriteResult', success: boolean, errors: Array<Types.SetDagRunFavoriteError>, dagRun?: { __typename?: 'DAGRun', id: string, label?: string | null, isFavorite: boolean } | null } | null };

export type PipelineRunFavoriteTrigger_RunFragment = { __typename?: 'DAGRun', id: string, label?: string | null, isFavorite: boolean };

export const PipelineRunFavoriteTrigger_RunFragmentDoc = gql`
    fragment PipelineRunFavoriteTrigger_run on DAGRun {
  id
  label
  isFavorite
  ...PipelineRunFavoriteIcon_run
}
    ${PipelineRunFavoriteIcon_RunFragmentDoc}`;
export const SetFavoriteRunDocument = gql`
    mutation setFavoriteRun($input: SetDAGRunFavoriteInput!) {
  setDAGRunFavorite(input: $input) {
    success
    errors
    dagRun {
      id
      label
      isFavorite
    }
  }
}
    `;
export type SetFavoriteRunMutationFn = Apollo.MutationFunction<SetFavoriteRunMutation, SetFavoriteRunMutationVariables>;

/**
 * __useSetFavoriteRunMutation__
 *
 * To run a mutation, you first call `useSetFavoriteRunMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useSetFavoriteRunMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [setFavoriteRunMutation, { data, loading, error }] = useSetFavoriteRunMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useSetFavoriteRunMutation(baseOptions?: Apollo.MutationHookOptions<SetFavoriteRunMutation, SetFavoriteRunMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<SetFavoriteRunMutation, SetFavoriteRunMutationVariables>(SetFavoriteRunDocument, options);
      }
export type SetFavoriteRunMutationHookResult = ReturnType<typeof useSetFavoriteRunMutation>;
export type SetFavoriteRunMutationResult = Apollo.MutationResult<SetFavoriteRunMutation>;
export type SetFavoriteRunMutationOptions = Apollo.BaseMutationOptions<SetFavoriteRunMutation, SetFavoriteRunMutationVariables>;