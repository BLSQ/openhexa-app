import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type ResetPasswordMutationVariables = Types.Exact<{
  input: Types.ResetPasswordInput;
}>;


export type ResetPasswordMutation = { __typename?: 'Mutation', resetPassword: { __typename?: 'ResetPasswordResult', success: boolean } };

export type SetPasswordMutationVariables = Types.Exact<{
  input: Types.SetPasswordInput;
}>;


export type SetPasswordMutation = { __typename?: 'Mutation', setPassword: { __typename?: 'SetPasswordResult', success: boolean, error?: Types.SetPasswordError | null } };

export type LoginMutationVariables = Types.Exact<{
  input: Types.LoginInput;
}>;


export type LoginMutation = { __typename?: 'Mutation', login: { __typename?: 'LoginResult', success: boolean, errors?: Array<Types.LoginError> | null } };

export type LogoutMutationVariables = Types.Exact<{ [key: string]: never; }>;


export type LogoutMutation = { __typename?: 'Mutation', logout: { __typename?: 'LogoutResult', success: boolean } };

export type RegisterMutationVariables = Types.Exact<{
  input: Types.RegisterInput;
}>;


export type RegisterMutation = { __typename?: 'Mutation', register: { __typename?: 'RegisterResult', success: boolean, errors?: Array<Types.RegisterError> | null } };

export type GenerateChallengeMutationVariables = Types.Exact<{ [key: string]: never; }>;


export type GenerateChallengeMutation = { __typename?: 'Mutation', generateChallenge: { __typename?: 'GenerateChallengeResult', success: boolean, errors?: Array<Types.GenerateChallengeError> | null } };

export type VerifyDeviceMutationVariables = Types.Exact<{
  input: Types.VerifyDeviceInput;
}>;


export type VerifyDeviceMutation = { __typename?: 'Mutation', verifyDevice: { __typename?: 'VerifyDeviceResult', success: boolean, errors?: Array<Types.VerifyDeviceError> | null } };

export type DisableTwoFactorMutationVariables = Types.Exact<{
  input: Types.DisableTwoFactorInput;
}>;


export type DisableTwoFactorMutation = { __typename?: 'Mutation', disableTwoFactor: { __typename?: 'DisableTwoFactorResult', success: boolean, errors?: Array<Types.DisableTwoFactorError> | null } };

export type EnableTwoFactorMutationVariables = Types.Exact<{ [key: string]: never; }>;


export type EnableTwoFactorMutation = { __typename?: 'Mutation', enableTwoFactor: { __typename?: 'EnableTwoFactorResult', success: boolean, verified?: boolean | null, errors?: Array<Types.EnableTwoFactorError> | null } };

export type UpdateUserMutationVariables = Types.Exact<{
  input: Types.UpdateUserInput;
}>;


export type UpdateUserMutation = { __typename?: 'Mutation', updateUser: { __typename?: 'UpdateUserResult', success: boolean, errors: Array<Types.UpdateUserError>, user?: { __typename?: 'User', id: string, language: string, firstName?: string | null, lastName?: string | null } | null } };


export const ResetPasswordDocument = gql`
    mutation ResetPassword($input: ResetPasswordInput!) {
  resetPassword(input: $input) {
    success
  }
}
    `;
export type ResetPasswordMutationFn = Apollo.MutationFunction<ResetPasswordMutation, ResetPasswordMutationVariables>;

/**
 * __useResetPasswordMutation__
 *
 * To run a mutation, you first call `useResetPasswordMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useResetPasswordMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [resetPasswordMutation, { data, loading, error }] = useResetPasswordMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useResetPasswordMutation(baseOptions?: Apollo.MutationHookOptions<ResetPasswordMutation, ResetPasswordMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<ResetPasswordMutation, ResetPasswordMutationVariables>(ResetPasswordDocument, options);
      }
export type ResetPasswordMutationHookResult = ReturnType<typeof useResetPasswordMutation>;
export type ResetPasswordMutationResult = Apollo.MutationResult<ResetPasswordMutation>;
export type ResetPasswordMutationOptions = Apollo.BaseMutationOptions<ResetPasswordMutation, ResetPasswordMutationVariables>;
export const SetPasswordDocument = gql`
    mutation SetPassword($input: SetPasswordInput!) {
  setPassword(input: $input) {
    success
    error
  }
}
    `;
export type SetPasswordMutationFn = Apollo.MutationFunction<SetPasswordMutation, SetPasswordMutationVariables>;

/**
 * __useSetPasswordMutation__
 *
 * To run a mutation, you first call `useSetPasswordMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useSetPasswordMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [setPasswordMutation, { data, loading, error }] = useSetPasswordMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useSetPasswordMutation(baseOptions?: Apollo.MutationHookOptions<SetPasswordMutation, SetPasswordMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<SetPasswordMutation, SetPasswordMutationVariables>(SetPasswordDocument, options);
      }
export type SetPasswordMutationHookResult = ReturnType<typeof useSetPasswordMutation>;
export type SetPasswordMutationResult = Apollo.MutationResult<SetPasswordMutation>;
export type SetPasswordMutationOptions = Apollo.BaseMutationOptions<SetPasswordMutation, SetPasswordMutationVariables>;
export const LoginDocument = gql`
    mutation Login($input: LoginInput!) {
  login(input: $input) {
    success
    errors
  }
}
    `;
export type LoginMutationFn = Apollo.MutationFunction<LoginMutation, LoginMutationVariables>;

/**
 * __useLoginMutation__
 *
 * To run a mutation, you first call `useLoginMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useLoginMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [loginMutation, { data, loading, error }] = useLoginMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useLoginMutation(baseOptions?: Apollo.MutationHookOptions<LoginMutation, LoginMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<LoginMutation, LoginMutationVariables>(LoginDocument, options);
      }
export type LoginMutationHookResult = ReturnType<typeof useLoginMutation>;
export type LoginMutationResult = Apollo.MutationResult<LoginMutation>;
export type LoginMutationOptions = Apollo.BaseMutationOptions<LoginMutation, LoginMutationVariables>;
export const LogoutDocument = gql`
    mutation Logout {
  logout {
    success
  }
}
    `;
export type LogoutMutationFn = Apollo.MutationFunction<LogoutMutation, LogoutMutationVariables>;

/**
 * __useLogoutMutation__
 *
 * To run a mutation, you first call `useLogoutMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useLogoutMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [logoutMutation, { data, loading, error }] = useLogoutMutation({
 *   variables: {
 *   },
 * });
 */
export function useLogoutMutation(baseOptions?: Apollo.MutationHookOptions<LogoutMutation, LogoutMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<LogoutMutation, LogoutMutationVariables>(LogoutDocument, options);
      }
export type LogoutMutationHookResult = ReturnType<typeof useLogoutMutation>;
export type LogoutMutationResult = Apollo.MutationResult<LogoutMutation>;
export type LogoutMutationOptions = Apollo.BaseMutationOptions<LogoutMutation, LogoutMutationVariables>;
export const RegisterDocument = gql`
    mutation Register($input: RegisterInput!) {
  register(input: $input) {
    success
    errors
  }
}
    `;
export type RegisterMutationFn = Apollo.MutationFunction<RegisterMutation, RegisterMutationVariables>;

/**
 * __useRegisterMutation__
 *
 * To run a mutation, you first call `useRegisterMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useRegisterMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [registerMutation, { data, loading, error }] = useRegisterMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useRegisterMutation(baseOptions?: Apollo.MutationHookOptions<RegisterMutation, RegisterMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<RegisterMutation, RegisterMutationVariables>(RegisterDocument, options);
      }
export type RegisterMutationHookResult = ReturnType<typeof useRegisterMutation>;
export type RegisterMutationResult = Apollo.MutationResult<RegisterMutation>;
export type RegisterMutationOptions = Apollo.BaseMutationOptions<RegisterMutation, RegisterMutationVariables>;
export const GenerateChallengeDocument = gql`
    mutation GenerateChallenge {
  generateChallenge {
    success
    errors
  }
}
    `;
export type GenerateChallengeMutationFn = Apollo.MutationFunction<GenerateChallengeMutation, GenerateChallengeMutationVariables>;

/**
 * __useGenerateChallengeMutation__
 *
 * To run a mutation, you first call `useGenerateChallengeMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useGenerateChallengeMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [generateChallengeMutation, { data, loading, error }] = useGenerateChallengeMutation({
 *   variables: {
 *   },
 * });
 */
export function useGenerateChallengeMutation(baseOptions?: Apollo.MutationHookOptions<GenerateChallengeMutation, GenerateChallengeMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<GenerateChallengeMutation, GenerateChallengeMutationVariables>(GenerateChallengeDocument, options);
      }
export type GenerateChallengeMutationHookResult = ReturnType<typeof useGenerateChallengeMutation>;
export type GenerateChallengeMutationResult = Apollo.MutationResult<GenerateChallengeMutation>;
export type GenerateChallengeMutationOptions = Apollo.BaseMutationOptions<GenerateChallengeMutation, GenerateChallengeMutationVariables>;
export const VerifyDeviceDocument = gql`
    mutation VerifyDevice($input: VerifyDeviceInput!) {
  verifyDevice(input: $input) {
    success
    errors
  }
}
    `;
export type VerifyDeviceMutationFn = Apollo.MutationFunction<VerifyDeviceMutation, VerifyDeviceMutationVariables>;

/**
 * __useVerifyDeviceMutation__
 *
 * To run a mutation, you first call `useVerifyDeviceMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useVerifyDeviceMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [verifyDeviceMutation, { data, loading, error }] = useVerifyDeviceMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useVerifyDeviceMutation(baseOptions?: Apollo.MutationHookOptions<VerifyDeviceMutation, VerifyDeviceMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<VerifyDeviceMutation, VerifyDeviceMutationVariables>(VerifyDeviceDocument, options);
      }
export type VerifyDeviceMutationHookResult = ReturnType<typeof useVerifyDeviceMutation>;
export type VerifyDeviceMutationResult = Apollo.MutationResult<VerifyDeviceMutation>;
export type VerifyDeviceMutationOptions = Apollo.BaseMutationOptions<VerifyDeviceMutation, VerifyDeviceMutationVariables>;
export const DisableTwoFactorDocument = gql`
    mutation DisableTwoFactor($input: DisableTwoFactorInput!) {
  disableTwoFactor(input: $input) {
    success
    errors
  }
}
    `;
export type DisableTwoFactorMutationFn = Apollo.MutationFunction<DisableTwoFactorMutation, DisableTwoFactorMutationVariables>;

/**
 * __useDisableTwoFactorMutation__
 *
 * To run a mutation, you first call `useDisableTwoFactorMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDisableTwoFactorMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [disableTwoFactorMutation, { data, loading, error }] = useDisableTwoFactorMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDisableTwoFactorMutation(baseOptions?: Apollo.MutationHookOptions<DisableTwoFactorMutation, DisableTwoFactorMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DisableTwoFactorMutation, DisableTwoFactorMutationVariables>(DisableTwoFactorDocument, options);
      }
export type DisableTwoFactorMutationHookResult = ReturnType<typeof useDisableTwoFactorMutation>;
export type DisableTwoFactorMutationResult = Apollo.MutationResult<DisableTwoFactorMutation>;
export type DisableTwoFactorMutationOptions = Apollo.BaseMutationOptions<DisableTwoFactorMutation, DisableTwoFactorMutationVariables>;
export const EnableTwoFactorDocument = gql`
    mutation EnableTwoFactor {
  enableTwoFactor {
    success
    verified
    errors
  }
}
    `;
export type EnableTwoFactorMutationFn = Apollo.MutationFunction<EnableTwoFactorMutation, EnableTwoFactorMutationVariables>;

/**
 * __useEnableTwoFactorMutation__
 *
 * To run a mutation, you first call `useEnableTwoFactorMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useEnableTwoFactorMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [enableTwoFactorMutation, { data, loading, error }] = useEnableTwoFactorMutation({
 *   variables: {
 *   },
 * });
 */
export function useEnableTwoFactorMutation(baseOptions?: Apollo.MutationHookOptions<EnableTwoFactorMutation, EnableTwoFactorMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<EnableTwoFactorMutation, EnableTwoFactorMutationVariables>(EnableTwoFactorDocument, options);
      }
export type EnableTwoFactorMutationHookResult = ReturnType<typeof useEnableTwoFactorMutation>;
export type EnableTwoFactorMutationResult = Apollo.MutationResult<EnableTwoFactorMutation>;
export type EnableTwoFactorMutationOptions = Apollo.BaseMutationOptions<EnableTwoFactorMutation, EnableTwoFactorMutationVariables>;
export const UpdateUserDocument = gql`
    mutation UpdateUser($input: UpdateUserInput!) {
  updateUser(input: $input) {
    success
    errors
    user {
      id
      language
      firstName
      lastName
    }
  }
}
    `;
export type UpdateUserMutationFn = Apollo.MutationFunction<UpdateUserMutation, UpdateUserMutationVariables>;

/**
 * __useUpdateUserMutation__
 *
 * To run a mutation, you first call `useUpdateUserMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateUserMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateUserMutation, { data, loading, error }] = useUpdateUserMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateUserMutation(baseOptions?: Apollo.MutationHookOptions<UpdateUserMutation, UpdateUserMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateUserMutation, UpdateUserMutationVariables>(UpdateUserDocument, options);
      }
export type UpdateUserMutationHookResult = ReturnType<typeof useUpdateUserMutation>;
export type UpdateUserMutationResult = Apollo.MutationResult<UpdateUserMutation>;
export type UpdateUserMutationOptions = Apollo.BaseMutationOptions<UpdateUserMutation, UpdateUserMutationVariables>;