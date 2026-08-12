import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import { UserAvatar_UserFragmentDoc } from '../features/UserAvatar.generated';
import { User_UserFragmentDoc } from '../../core/features/User/User.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type GetUserQueryVariables = Types.Exact<{ [key: string]: never; }>;


export type GetUserQuery = { __typename?: 'Query', me: { __typename?: 'Me', hasTwoFactorEnabled: boolean, permissions: { __typename?: 'MePermissions', adminPanel: boolean, superUser: boolean }, features: Array<{ __typename?: 'FeatureFlag', code: string }>, user?: { __typename?: 'User', email: string, id: string, firstName?: string | null, lastName?: string | null, displayName: string, language: string, dateJoined: any, analyticsEnabled: boolean, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null } };

export type AccountPageQueryVariables = Types.Exact<{ [key: string]: never; }>;


export type AccountPageQuery = { __typename?: 'Query', me: { __typename?: 'Me', hasTwoFactorEnabled: boolean, user?: { __typename?: 'User', firstName?: string | null, lastName?: string | null, dateJoined: any, displayName: string, id: string, email: string, language: string, analyticsEnabled: boolean, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null }, pendingWorkspaceInvitations: { __typename?: 'WorkspaceInvitationPage', totalItems: number, items: Array<{ __typename?: 'WorkspaceInvitation', id: string, status: Types.WorkspaceInvitationStatus, role: Types.WorkspaceMembershipRole, createdAt: any, invitedBy?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null, workspace: { __typename?: 'Workspace', slug: string, name: string } }> } };

export type AccountAccessTokensQueryVariables = Types.Exact<{
  page: Types.Scalars['Int']['input'];
  perPage: Types.Scalars['Int']['input'];
}>;


export type AccountAccessTokensQuery = { __typename?: 'Query', workspaces: { __typename?: 'WorkspacePage', totalItems: number, items: Array<{ __typename?: 'Workspace', slug: string, name: string, currentMembership?: { __typename?: 'WorkspaceMembership', role: Types.WorkspaceMembershipRole } | null, permissions: { __typename?: 'WorkspacePermissions', generateToken: boolean } }> } };

export type RegisterPageQueryVariables = Types.Exact<{ [key: string]: never; }>;


export type RegisterPageQuery = { __typename?: 'Query', config: { __typename?: 'Config', passwordRequirements?: Array<string> | null, passwordLoginEnabled: boolean, oidcProviders: Array<{ __typename?: 'OidcProvider', id: string, displayName: string, loginUrl: string }> } };

export type SignupPageQueryVariables = Types.Exact<{ [key: string]: never; }>;


export type SignupPageQuery = { __typename?: 'Query', config: { __typename?: 'Config', allowSelfRegistration: boolean, passwordLoginEnabled: boolean, oidcProviders: Array<{ __typename?: 'OidcProvider', id: string, displayName: string, loginUrl: string }> } };


export const GetUserDocument = gql`
    query GetUser {
  me {
    hasTwoFactorEnabled
    permissions {
      adminPanel
      superUser
    }
    features {
      code
    }
    user {
      ...UserAvatar_user
      email
      id
      firstName
      lastName
      displayName
      language
      dateJoined
      analyticsEnabled
      avatar {
        initials
        color
      }
    }
  }
}
    ${UserAvatar_UserFragmentDoc}`;

/**
 * __useGetUserQuery__
 *
 * To run a query within a React component, call `useGetUserQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetUserQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetUserQuery({
 *   variables: {
 *   },
 * });
 */
export function useGetUserQuery(baseOptions?: Apollo.QueryHookOptions<GetUserQuery, GetUserQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetUserQuery, GetUserQueryVariables>(GetUserDocument, options);
      }
export function useGetUserLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetUserQuery, GetUserQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetUserQuery, GetUserQueryVariables>(GetUserDocument, options);
        }
export function useGetUserSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetUserQuery, GetUserQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetUserQuery, GetUserQueryVariables>(GetUserDocument, options);
        }
export type GetUserQueryHookResult = ReturnType<typeof useGetUserQuery>;
export type GetUserLazyQueryHookResult = ReturnType<typeof useGetUserLazyQuery>;
export type GetUserSuspenseQueryHookResult = ReturnType<typeof useGetUserSuspenseQuery>;
export type GetUserQueryResult = Apollo.QueryResult<GetUserQuery, GetUserQueryVariables>;
export const AccountPageDocument = gql`
    query AccountPage {
  me {
    hasTwoFactorEnabled
    user {
      firstName
      lastName
      dateJoined
      displayName
      id
      email
      language
      analyticsEnabled
      ...User_user
    }
  }
  pendingWorkspaceInvitations {
    totalItems
    items {
      id
      status
      invitedBy {
        ...User_user
      }
      role
      workspace {
        slug
        name
      }
      createdAt
    }
  }
}
    ${User_UserFragmentDoc}`;

/**
 * __useAccountPageQuery__
 *
 * To run a query within a React component, call `useAccountPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useAccountPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAccountPageQuery({
 *   variables: {
 *   },
 * });
 */
export function useAccountPageQuery(baseOptions?: Apollo.QueryHookOptions<AccountPageQuery, AccountPageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<AccountPageQuery, AccountPageQueryVariables>(AccountPageDocument, options);
      }
export function useAccountPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<AccountPageQuery, AccountPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<AccountPageQuery, AccountPageQueryVariables>(AccountPageDocument, options);
        }
export function useAccountPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<AccountPageQuery, AccountPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<AccountPageQuery, AccountPageQueryVariables>(AccountPageDocument, options);
        }
export type AccountPageQueryHookResult = ReturnType<typeof useAccountPageQuery>;
export type AccountPageLazyQueryHookResult = ReturnType<typeof useAccountPageLazyQuery>;
export type AccountPageSuspenseQueryHookResult = ReturnType<typeof useAccountPageSuspenseQuery>;
export type AccountPageQueryResult = Apollo.QueryResult<AccountPageQuery, AccountPageQueryVariables>;
export const AccountAccessTokensDocument = gql`
    query AccountAccessTokens($page: Int!, $perPage: Int!) {
  workspaces(page: $page, perPage: $perPage) {
    totalItems
    items {
      slug
      name
      currentMembership {
        role
      }
      permissions {
        generateToken
      }
    }
  }
}
    `;

/**
 * __useAccountAccessTokensQuery__
 *
 * To run a query within a React component, call `useAccountAccessTokensQuery` and pass it any options that fit your needs.
 * When your component renders, `useAccountAccessTokensQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAccountAccessTokensQuery({
 *   variables: {
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useAccountAccessTokensQuery(baseOptions: Apollo.QueryHookOptions<AccountAccessTokensQuery, AccountAccessTokensQueryVariables> & ({ variables: AccountAccessTokensQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<AccountAccessTokensQuery, AccountAccessTokensQueryVariables>(AccountAccessTokensDocument, options);
      }
export function useAccountAccessTokensLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<AccountAccessTokensQuery, AccountAccessTokensQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<AccountAccessTokensQuery, AccountAccessTokensQueryVariables>(AccountAccessTokensDocument, options);
        }
export function useAccountAccessTokensSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<AccountAccessTokensQuery, AccountAccessTokensQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<AccountAccessTokensQuery, AccountAccessTokensQueryVariables>(AccountAccessTokensDocument, options);
        }
export type AccountAccessTokensQueryHookResult = ReturnType<typeof useAccountAccessTokensQuery>;
export type AccountAccessTokensLazyQueryHookResult = ReturnType<typeof useAccountAccessTokensLazyQuery>;
export type AccountAccessTokensSuspenseQueryHookResult = ReturnType<typeof useAccountAccessTokensSuspenseQuery>;
export type AccountAccessTokensQueryResult = Apollo.QueryResult<AccountAccessTokensQuery, AccountAccessTokensQueryVariables>;
export const RegisterPageDocument = gql`
    query RegisterPage {
  config {
    passwordRequirements
    passwordLoginEnabled
    oidcProviders {
      id
      displayName
      loginUrl
    }
  }
}
    `;

/**
 * __useRegisterPageQuery__
 *
 * To run a query within a React component, call `useRegisterPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useRegisterPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useRegisterPageQuery({
 *   variables: {
 *   },
 * });
 */
export function useRegisterPageQuery(baseOptions?: Apollo.QueryHookOptions<RegisterPageQuery, RegisterPageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<RegisterPageQuery, RegisterPageQueryVariables>(RegisterPageDocument, options);
      }
export function useRegisterPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<RegisterPageQuery, RegisterPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<RegisterPageQuery, RegisterPageQueryVariables>(RegisterPageDocument, options);
        }
export function useRegisterPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<RegisterPageQuery, RegisterPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<RegisterPageQuery, RegisterPageQueryVariables>(RegisterPageDocument, options);
        }
export type RegisterPageQueryHookResult = ReturnType<typeof useRegisterPageQuery>;
export type RegisterPageLazyQueryHookResult = ReturnType<typeof useRegisterPageLazyQuery>;
export type RegisterPageSuspenseQueryHookResult = ReturnType<typeof useRegisterPageSuspenseQuery>;
export type RegisterPageQueryResult = Apollo.QueryResult<RegisterPageQuery, RegisterPageQueryVariables>;
export const SignupPageDocument = gql`
    query SignupPage {
  config {
    allowSelfRegistration
    passwordLoginEnabled
    oidcProviders {
      id
      displayName
      loginUrl
    }
  }
}
    `;

/**
 * __useSignupPageQuery__
 *
 * To run a query within a React component, call `useSignupPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useSignupPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useSignupPageQuery({
 *   variables: {
 *   },
 * });
 */
export function useSignupPageQuery(baseOptions?: Apollo.QueryHookOptions<SignupPageQuery, SignupPageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<SignupPageQuery, SignupPageQueryVariables>(SignupPageDocument, options);
      }
export function useSignupPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<SignupPageQuery, SignupPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<SignupPageQuery, SignupPageQueryVariables>(SignupPageDocument, options);
        }
export function useSignupPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<SignupPageQuery, SignupPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<SignupPageQuery, SignupPageQueryVariables>(SignupPageDocument, options);
        }
export type SignupPageQueryHookResult = ReturnType<typeof useSignupPageQuery>;
export type SignupPageLazyQueryHookResult = ReturnType<typeof useSignupPageLazyQuery>;
export type SignupPageSuspenseQueryHookResult = ReturnType<typeof useSignupPageSuspenseQuery>;
export type SignupPageQueryResult = Apollo.QueryResult<SignupPageQuery, SignupPageQueryVariables>;