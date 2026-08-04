import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { UserColumn_UserFragmentDoc } from '../../../core/components/DataGrid/UserColumn.generated';
import { User_UserFragmentDoc } from '../../../core/features/User/User.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type SavedQueryListItem_SavedQueryFragment = { __typename?: 'SavedQuery', id: string, name: string, description?: string | null, updatedAt: any, visibility: Types.SavedQueryVisibility, createdBy?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null, permissions: { __typename?: 'SavedQueryPermissions', update: boolean, delete: boolean, updateVisibility: boolean } };

export type SavedQuery_SavedQueryFragment = { __typename?: 'SavedQuery', id: string, name: string, description?: string | null, content: string, updatedAt: any, visibility: Types.SavedQueryVisibility, createdBy?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null, permissions: { __typename?: 'SavedQueryPermissions', update: boolean, delete: boolean, updateVisibility: boolean } };

export type CreateSavedQueryMutationVariables = Types.Exact<{
  input: Types.CreateSavedQueryInput;
}>;


export type CreateSavedQueryMutation = { __typename?: 'Mutation', createSavedQuery: { __typename?: 'CreateSavedQueryResult', success: boolean, errors: Array<Types.CreateSavedQueryError>, savedQuery?: { __typename?: 'SavedQuery', id: string, name: string, description?: string | null, content: string, updatedAt: any, visibility: Types.SavedQueryVisibility, createdBy?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null, permissions: { __typename?: 'SavedQueryPermissions', update: boolean, delete: boolean, updateVisibility: boolean } } | null } };

export type UpdateSavedQueryMutationVariables = Types.Exact<{
  input: Types.UpdateSavedQueryInput;
}>;


export type UpdateSavedQueryMutation = { __typename?: 'Mutation', updateSavedQuery: { __typename?: 'UpdateSavedQueryResult', success: boolean, errors: Array<Types.UpdateSavedQueryError>, savedQuery?: { __typename?: 'SavedQuery', id: string, name: string, description?: string | null, content: string, updatedAt: any, visibility: Types.SavedQueryVisibility, createdBy?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null, permissions: { __typename?: 'SavedQueryPermissions', update: boolean, delete: boolean, updateVisibility: boolean } } | null } };

export type DeleteSavedQueryMutationVariables = Types.Exact<{
  input: Types.DeleteSavedQueryInput;
}>;


export type DeleteSavedQueryMutation = { __typename?: 'Mutation', deleteSavedQuery: { __typename?: 'DeleteSavedQueryResult', success: boolean, errors: Array<Types.DeleteSavedQueryError> } };

export const SavedQueryListItem_SavedQueryFragmentDoc = gql`
    fragment SavedQueryListItem_savedQuery on SavedQuery {
  id
  name
  description
  updatedAt
  visibility
  createdBy {
    ...UserColumn_user
  }
  permissions {
    update
    delete
    updateVisibility
  }
}
    ${UserColumn_UserFragmentDoc}`;
export const SavedQuery_SavedQueryFragmentDoc = gql`
    fragment SavedQuery_savedQuery on SavedQuery {
  id
  name
  description
  content
  updatedAt
  visibility
  createdBy {
    ...User_user
  }
  permissions {
    update
    delete
    updateVisibility
  }
}
    ${User_UserFragmentDoc}`;
export const CreateSavedQueryDocument = gql`
    mutation createSavedQuery($input: CreateSavedQueryInput!) {
  createSavedQuery(input: $input) {
    success
    errors
    savedQuery {
      ...SavedQuery_savedQuery
    }
  }
}
    ${SavedQuery_SavedQueryFragmentDoc}`;
export type CreateSavedQueryMutationFn = Apollo.MutationFunction<CreateSavedQueryMutation, CreateSavedQueryMutationVariables>;

/**
 * __useCreateSavedQueryMutation__
 *
 * To run a mutation, you first call `useCreateSavedQueryMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateSavedQueryMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createSavedQueryMutation, { data, loading, error }] = useCreateSavedQueryMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useCreateSavedQueryMutation(baseOptions?: Apollo.MutationHookOptions<CreateSavedQueryMutation, CreateSavedQueryMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<CreateSavedQueryMutation, CreateSavedQueryMutationVariables>(CreateSavedQueryDocument, options);
      }
export type CreateSavedQueryMutationHookResult = ReturnType<typeof useCreateSavedQueryMutation>;
export type CreateSavedQueryMutationResult = Apollo.MutationResult<CreateSavedQueryMutation>;
export type CreateSavedQueryMutationOptions = Apollo.BaseMutationOptions<CreateSavedQueryMutation, CreateSavedQueryMutationVariables>;
export const UpdateSavedQueryDocument = gql`
    mutation updateSavedQuery($input: UpdateSavedQueryInput!) {
  updateSavedQuery(input: $input) {
    success
    errors
    savedQuery {
      ...SavedQuery_savedQuery
    }
  }
}
    ${SavedQuery_SavedQueryFragmentDoc}`;
export type UpdateSavedQueryMutationFn = Apollo.MutationFunction<UpdateSavedQueryMutation, UpdateSavedQueryMutationVariables>;

/**
 * __useUpdateSavedQueryMutation__
 *
 * To run a mutation, you first call `useUpdateSavedQueryMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateSavedQueryMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateSavedQueryMutation, { data, loading, error }] = useUpdateSavedQueryMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateSavedQueryMutation(baseOptions?: Apollo.MutationHookOptions<UpdateSavedQueryMutation, UpdateSavedQueryMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateSavedQueryMutation, UpdateSavedQueryMutationVariables>(UpdateSavedQueryDocument, options);
      }
export type UpdateSavedQueryMutationHookResult = ReturnType<typeof useUpdateSavedQueryMutation>;
export type UpdateSavedQueryMutationResult = Apollo.MutationResult<UpdateSavedQueryMutation>;
export type UpdateSavedQueryMutationOptions = Apollo.BaseMutationOptions<UpdateSavedQueryMutation, UpdateSavedQueryMutationVariables>;
export const DeleteSavedQueryDocument = gql`
    mutation deleteSavedQuery($input: DeleteSavedQueryInput!) {
  deleteSavedQuery(input: $input) {
    success
    errors
  }
}
    `;
export type DeleteSavedQueryMutationFn = Apollo.MutationFunction<DeleteSavedQueryMutation, DeleteSavedQueryMutationVariables>;

/**
 * __useDeleteSavedQueryMutation__
 *
 * To run a mutation, you first call `useDeleteSavedQueryMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteSavedQueryMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteSavedQueryMutation, { data, loading, error }] = useDeleteSavedQueryMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeleteSavedQueryMutation(baseOptions?: Apollo.MutationHookOptions<DeleteSavedQueryMutation, DeleteSavedQueryMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeleteSavedQueryMutation, DeleteSavedQueryMutationVariables>(DeleteSavedQueryDocument, options);
      }
export type DeleteSavedQueryMutationHookResult = ReturnType<typeof useDeleteSavedQueryMutation>;
export type DeleteSavedQueryMutationResult = Apollo.MutationResult<DeleteSavedQueryMutation>;
export type DeleteSavedQueryMutationOptions = Apollo.BaseMutationOptions<DeleteSavedQueryMutation, DeleteSavedQueryMutationVariables>;