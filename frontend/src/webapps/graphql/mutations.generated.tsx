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

export type AddWebappToShortcutsMutationVariables = Types.Exact<{
  input: Types.AddWebappToShortcutsInput;
}>;


export type AddWebappToShortcutsMutation = { __typename?: 'Mutation', addWebappToShortcuts: { __typename?: 'AddWebappToShortcutsResult', success: boolean, errors: Array<Types.AddWebappToShortcutsError> } };

export type RemoveWebappFromShortcutsMutationVariables = Types.Exact<{
  input: Types.RemoveWebappFromShortcutsInput;
}>;


export type RemoveWebappFromShortcutsMutation = { __typename?: 'Mutation', removeWebappFromShortcuts: { __typename?: 'RemoveWebappFromShortcutsResult', success: boolean, errors: Array<Types.RemoveWebappFromShortcutsError> } };


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
export const AddWebappToShortcutsDocument = gql`
    mutation AddWebappToShortcuts($input: AddWebappToShortcutsInput!) {
  addWebappToShortcuts(input: $input) {
    success
    errors
  }
}
    `;
export type AddWebappToShortcutsMutationFn = Apollo.MutationFunction<AddWebappToShortcutsMutation, AddWebappToShortcutsMutationVariables>;

/**
 * __useAddWebappToShortcutsMutation__
 *
 * To run a mutation, you first call `useAddWebappToShortcutsMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useAddWebappToShortcutsMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [addWebappToShortcutsMutation, { data, loading, error }] = useAddWebappToShortcutsMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useAddWebappToShortcutsMutation(baseOptions?: Apollo.MutationHookOptions<AddWebappToShortcutsMutation, AddWebappToShortcutsMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<AddWebappToShortcutsMutation, AddWebappToShortcutsMutationVariables>(AddWebappToShortcutsDocument, options);
      }
export type AddWebappToShortcutsMutationHookResult = ReturnType<typeof useAddWebappToShortcutsMutation>;
export type AddWebappToShortcutsMutationResult = Apollo.MutationResult<AddWebappToShortcutsMutation>;
export type AddWebappToShortcutsMutationOptions = Apollo.BaseMutationOptions<AddWebappToShortcutsMutation, AddWebappToShortcutsMutationVariables>;
export const RemoveWebappFromShortcutsDocument = gql`
    mutation RemoveWebappFromShortcuts($input: RemoveWebappFromShortcutsInput!) {
  removeWebappFromShortcuts(input: $input) {
    success
    errors
  }
}
    `;
export type RemoveWebappFromShortcutsMutationFn = Apollo.MutationFunction<RemoveWebappFromShortcutsMutation, RemoveWebappFromShortcutsMutationVariables>;

/**
 * __useRemoveWebappFromShortcutsMutation__
 *
 * To run a mutation, you first call `useRemoveWebappFromShortcutsMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useRemoveWebappFromShortcutsMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [removeWebappFromShortcutsMutation, { data, loading, error }] = useRemoveWebappFromShortcutsMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useRemoveWebappFromShortcutsMutation(baseOptions?: Apollo.MutationHookOptions<RemoveWebappFromShortcutsMutation, RemoveWebappFromShortcutsMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<RemoveWebappFromShortcutsMutation, RemoveWebappFromShortcutsMutationVariables>(RemoveWebappFromShortcutsDocument, options);
      }
export type RemoveWebappFromShortcutsMutationHookResult = ReturnType<typeof useRemoveWebappFromShortcutsMutation>;
export type RemoveWebappFromShortcutsMutationResult = Apollo.MutationResult<RemoveWebappFromShortcutsMutation>;
export type RemoveWebappFromShortcutsMutationOptions = Apollo.BaseMutationOptions<RemoveWebappFromShortcutsMutation, RemoveWebappFromShortcutsMutationVariables>;