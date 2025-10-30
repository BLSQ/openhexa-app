import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type UpdateWebappMutationVariables = Types.Exact<{
  input: Types.UpdateWebappInput;
}>;


export type UpdateWebappMutation = { __typename?: 'Mutation', updateWebapp: { __typename?: 'UpdateWebappResult', success: boolean, errors: Array<Types.UpdateWebappError> } };

export type CreateWebappMutationVariables = Types.Exact<{
  input: Types.CreateWebappInput;
}>;


export type CreateWebappMutation = { __typename?: 'Mutation', createWebapp: { __typename?: 'CreateWebappResult', success: boolean, errors: Array<Types.CreateWebappError>, webapp?: { __typename?: 'Webapp', id: string } | null } };

export type AddToFavoritesMutationVariables = Types.Exact<{
  input: Types.AddToFavoritesInput;
}>;


export type AddToFavoritesMutation = { __typename?: 'Mutation', addToFavorites: { __typename?: 'AddToFavoritesResult', success: boolean, errors: Array<Types.AddToFavoritesError> } };

export type RemoveFromFavoritesMutationVariables = Types.Exact<{
  input: Types.RemoveFromFavoritesInput;
}>;


export type RemoveFromFavoritesMutation = { __typename?: 'Mutation', removeFromFavorites: { __typename?: 'RemoveFromFavoritesResult', success: boolean, errors: Array<Types.RemoveFromFavoritesError> } };

export type AddToShortcutsMutationVariables = Types.Exact<{
  input: Types.AddToShortcutsInput;
}>;


export type AddToShortcutsMutation = { __typename?: 'Mutation', addToShortcuts: { __typename?: 'AddToShortcutsResult', success: boolean, errors: Array<Types.AddToShortcutsError> } };

export type RemoveFromShortcutsMutationVariables = Types.Exact<{
  input: Types.RemoveFromShortcutsInput;
}>;


export type RemoveFromShortcutsMutation = { __typename?: 'Mutation', removeFromShortcuts: { __typename?: 'RemoveFromShortcutsResult', success: boolean, errors: Array<Types.RemoveFromShortcutsError> } };


export const UpdateWebappDocument = gql`
    mutation UpdateWebapp($input: UpdateWebappInput!) {
  updateWebapp(input: $input) {
    success
    errors
  }
}
    `;
export type UpdateWebappMutationFn = Apollo.MutationFunction<UpdateWebappMutation, UpdateWebappMutationVariables>;

/**
 * __useUpdateWebappMutation__
 *
 * To run a mutation, you first call `useUpdateWebappMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateWebappMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateWebappMutation, { data, loading, error }] = useUpdateWebappMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateWebappMutation(baseOptions?: Apollo.MutationHookOptions<UpdateWebappMutation, UpdateWebappMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateWebappMutation, UpdateWebappMutationVariables>(UpdateWebappDocument, options);
      }
export type UpdateWebappMutationHookResult = ReturnType<typeof useUpdateWebappMutation>;
export type UpdateWebappMutationResult = Apollo.MutationResult<UpdateWebappMutation>;
export type UpdateWebappMutationOptions = Apollo.BaseMutationOptions<UpdateWebappMutation, UpdateWebappMutationVariables>;
export const CreateWebappDocument = gql`
    mutation CreateWebapp($input: CreateWebappInput!) {
  createWebapp(input: $input) {
    success
    errors
    webapp {
      id
    }
  }
}
    `;
export type CreateWebappMutationFn = Apollo.MutationFunction<CreateWebappMutation, CreateWebappMutationVariables>;

/**
 * __useCreateWebappMutation__
 *
 * To run a mutation, you first call `useCreateWebappMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateWebappMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createWebappMutation, { data, loading, error }] = useCreateWebappMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useCreateWebappMutation(baseOptions?: Apollo.MutationHookOptions<CreateWebappMutation, CreateWebappMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<CreateWebappMutation, CreateWebappMutationVariables>(CreateWebappDocument, options);
      }
export type CreateWebappMutationHookResult = ReturnType<typeof useCreateWebappMutation>;
export type CreateWebappMutationResult = Apollo.MutationResult<CreateWebappMutation>;
export type CreateWebappMutationOptions = Apollo.BaseMutationOptions<CreateWebappMutation, CreateWebappMutationVariables>;
export const AddToFavoritesDocument = gql`
    mutation AddToFavorites($input: AddToFavoritesInput!) {
  addToFavorites(input: $input) {
    success
    errors
  }
}
    `;
export type AddToFavoritesMutationFn = Apollo.MutationFunction<AddToFavoritesMutation, AddToFavoritesMutationVariables>;

/**
 * __useAddToFavoritesMutation__
 *
 * To run a mutation, you first call `useAddToFavoritesMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useAddToFavoritesMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [addToFavoritesMutation, { data, loading, error }] = useAddToFavoritesMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useAddToFavoritesMutation(baseOptions?: Apollo.MutationHookOptions<AddToFavoritesMutation, AddToFavoritesMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<AddToFavoritesMutation, AddToFavoritesMutationVariables>(AddToFavoritesDocument, options);
      }
export type AddToFavoritesMutationHookResult = ReturnType<typeof useAddToFavoritesMutation>;
export type AddToFavoritesMutationResult = Apollo.MutationResult<AddToFavoritesMutation>;
export type AddToFavoritesMutationOptions = Apollo.BaseMutationOptions<AddToFavoritesMutation, AddToFavoritesMutationVariables>;
export const RemoveFromFavoritesDocument = gql`
    mutation RemoveFromFavorites($input: RemoveFromFavoritesInput!) {
  removeFromFavorites(input: $input) {
    success
    errors
  }
}
    `;
export type RemoveFromFavoritesMutationFn = Apollo.MutationFunction<RemoveFromFavoritesMutation, RemoveFromFavoritesMutationVariables>;

/**
 * __useRemoveFromFavoritesMutation__
 *
 * To run a mutation, you first call `useRemoveFromFavoritesMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useRemoveFromFavoritesMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [removeFromFavoritesMutation, { data, loading, error }] = useRemoveFromFavoritesMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useRemoveFromFavoritesMutation(baseOptions?: Apollo.MutationHookOptions<RemoveFromFavoritesMutation, RemoveFromFavoritesMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<RemoveFromFavoritesMutation, RemoveFromFavoritesMutationVariables>(RemoveFromFavoritesDocument, options);
      }
export type RemoveFromFavoritesMutationHookResult = ReturnType<typeof useRemoveFromFavoritesMutation>;
export type RemoveFromFavoritesMutationResult = Apollo.MutationResult<RemoveFromFavoritesMutation>;
export type RemoveFromFavoritesMutationOptions = Apollo.BaseMutationOptions<RemoveFromFavoritesMutation, RemoveFromFavoritesMutationVariables>;
export const AddToShortcutsDocument = gql`
    mutation AddToShortcuts($input: AddToShortcutsInput!) {
  addToShortcuts(input: $input) {
    success
    errors
  }
}
    `;
export type AddToShortcutsMutationFn = Apollo.MutationFunction<AddToShortcutsMutation, AddToShortcutsMutationVariables>;

/**
 * __useAddToShortcutsMutation__
 *
 * To run a mutation, you first call `useAddToShortcutsMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useAddToShortcutsMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [addToShortcutsMutation, { data, loading, error }] = useAddToShortcutsMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useAddToShortcutsMutation(baseOptions?: Apollo.MutationHookOptions<AddToShortcutsMutation, AddToShortcutsMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<AddToShortcutsMutation, AddToShortcutsMutationVariables>(AddToShortcutsDocument, options);
      }
export type AddToShortcutsMutationHookResult = ReturnType<typeof useAddToShortcutsMutation>;
export type AddToShortcutsMutationResult = Apollo.MutationResult<AddToShortcutsMutation>;
export type AddToShortcutsMutationOptions = Apollo.BaseMutationOptions<AddToShortcutsMutation, AddToShortcutsMutationVariables>;
export const RemoveFromShortcutsDocument = gql`
    mutation RemoveFromShortcuts($input: RemoveFromShortcutsInput!) {
  removeFromShortcuts(input: $input) {
    success
    errors
  }
}
    `;
export type RemoveFromShortcutsMutationFn = Apollo.MutationFunction<RemoveFromShortcutsMutation, RemoveFromShortcutsMutationVariables>;

/**
 * __useRemoveFromShortcutsMutation__
 *
 * To run a mutation, you first call `useRemoveFromShortcutsMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useRemoveFromShortcutsMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [removeFromShortcutsMutation, { data, loading, error }] = useRemoveFromShortcutsMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useRemoveFromShortcutsMutation(baseOptions?: Apollo.MutationHookOptions<RemoveFromShortcutsMutation, RemoveFromShortcutsMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<RemoveFromShortcutsMutation, RemoveFromShortcutsMutationVariables>(RemoveFromShortcutsDocument, options);
      }
export type RemoveFromShortcutsMutationHookResult = ReturnType<typeof useRemoveFromShortcutsMutation>;
export type RemoveFromShortcutsMutationResult = Apollo.MutationResult<RemoveFromShortcutsMutation>;
export type RemoveFromShortcutsMutationOptions = Apollo.BaseMutationOptions<RemoveFromShortcutsMutation, RemoveFromShortcutsMutationVariables>;