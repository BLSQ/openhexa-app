import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import { McpConnection_ConnectionFragmentDoc } from './queries.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type UpdateMcpConnectionMutationVariables = Types.Exact<{
  input: Types.UpdateMcpConnectionInput;
}>;


export type UpdateMcpConnectionMutation = { __typename?: 'Mutation', updateMCPConnection: { __typename?: 'UpdateMCPConnectionResult', success: boolean, errors: Array<Types.UpdateMcpConnectionError>, mcpConnection?: { __typename?: 'MCPConnection', id: string, name: string, createdAt: any, lastUsedAt?: any | null, tools: Array<string>, workspaces: Array<{ __typename?: 'Workspace', slug: string, name: string }> } | null } };

export type RevokeMcpConnectionMutationVariables = Types.Exact<{
  input: Types.RevokeMcpConnectionInput;
}>;


export type RevokeMcpConnectionMutation = { __typename?: 'Mutation', revokeMCPConnection: { __typename?: 'RevokeMCPConnectionResult', success: boolean, errors: Array<Types.RevokeMcpConnectionError> } };

export type AuthorizeMcpConnectionMutationVariables = Types.Exact<{
  input: Types.AuthorizeMcpConnectionInput;
}>;


export type AuthorizeMcpConnectionMutation = { __typename?: 'Mutation', authorizeMCPConnection: { __typename?: 'AuthorizeMCPConnectionResult', success: boolean, errors: Array<Types.AuthorizeMcpConnectionError> } };


export const UpdateMcpConnectionDocument = gql`
    mutation UpdateMCPConnection($input: UpdateMCPConnectionInput!) {
  updateMCPConnection(input: $input) {
    success
    errors
    mcpConnection {
      ...MCPConnection_connection
    }
  }
}
    ${McpConnection_ConnectionFragmentDoc}`;
export type UpdateMcpConnectionMutationFn = Apollo.MutationFunction<UpdateMcpConnectionMutation, UpdateMcpConnectionMutationVariables>;

/**
 * __useUpdateMcpConnectionMutation__
 *
 * To run a mutation, you first call `useUpdateMcpConnectionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateMcpConnectionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateMcpConnectionMutation, { data, loading, error }] = useUpdateMcpConnectionMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateMcpConnectionMutation(baseOptions?: Apollo.MutationHookOptions<UpdateMcpConnectionMutation, UpdateMcpConnectionMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateMcpConnectionMutation, UpdateMcpConnectionMutationVariables>(UpdateMcpConnectionDocument, options);
      }
export type UpdateMcpConnectionMutationHookResult = ReturnType<typeof useUpdateMcpConnectionMutation>;
export type UpdateMcpConnectionMutationResult = Apollo.MutationResult<UpdateMcpConnectionMutation>;
export type UpdateMcpConnectionMutationOptions = Apollo.BaseMutationOptions<UpdateMcpConnectionMutation, UpdateMcpConnectionMutationVariables>;
export const RevokeMcpConnectionDocument = gql`
    mutation RevokeMCPConnection($input: RevokeMCPConnectionInput!) {
  revokeMCPConnection(input: $input) {
    success
    errors
  }
}
    `;
export type RevokeMcpConnectionMutationFn = Apollo.MutationFunction<RevokeMcpConnectionMutation, RevokeMcpConnectionMutationVariables>;

/**
 * __useRevokeMcpConnectionMutation__
 *
 * To run a mutation, you first call `useRevokeMcpConnectionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useRevokeMcpConnectionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [revokeMcpConnectionMutation, { data, loading, error }] = useRevokeMcpConnectionMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useRevokeMcpConnectionMutation(baseOptions?: Apollo.MutationHookOptions<RevokeMcpConnectionMutation, RevokeMcpConnectionMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<RevokeMcpConnectionMutation, RevokeMcpConnectionMutationVariables>(RevokeMcpConnectionDocument, options);
      }
export type RevokeMcpConnectionMutationHookResult = ReturnType<typeof useRevokeMcpConnectionMutation>;
export type RevokeMcpConnectionMutationResult = Apollo.MutationResult<RevokeMcpConnectionMutation>;
export type RevokeMcpConnectionMutationOptions = Apollo.BaseMutationOptions<RevokeMcpConnectionMutation, RevokeMcpConnectionMutationVariables>;
export const AuthorizeMcpConnectionDocument = gql`
    mutation AuthorizeMCPConnection($input: AuthorizeMCPConnectionInput!) {
  authorizeMCPConnection(input: $input) {
    success
    errors
  }
}
    `;
export type AuthorizeMcpConnectionMutationFn = Apollo.MutationFunction<AuthorizeMcpConnectionMutation, AuthorizeMcpConnectionMutationVariables>;

/**
 * __useAuthorizeMcpConnectionMutation__
 *
 * To run a mutation, you first call `useAuthorizeMcpConnectionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useAuthorizeMcpConnectionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [authorizeMcpConnectionMutation, { data, loading, error }] = useAuthorizeMcpConnectionMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useAuthorizeMcpConnectionMutation(baseOptions?: Apollo.MutationHookOptions<AuthorizeMcpConnectionMutation, AuthorizeMcpConnectionMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<AuthorizeMcpConnectionMutation, AuthorizeMcpConnectionMutationVariables>(AuthorizeMcpConnectionDocument, options);
      }
export type AuthorizeMcpConnectionMutationHookResult = ReturnType<typeof useAuthorizeMcpConnectionMutation>;
export type AuthorizeMcpConnectionMutationResult = Apollo.MutationResult<AuthorizeMcpConnectionMutation>;
export type AuthorizeMcpConnectionMutationOptions = Apollo.BaseMutationOptions<AuthorizeMcpConnectionMutation, AuthorizeMcpConnectionMutationVariables>;