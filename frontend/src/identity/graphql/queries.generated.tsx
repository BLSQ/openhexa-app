import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import { UserAvatar_UserFragmentDoc } from '../features/UserAvatar.generated';
import { User_UserFragmentDoc } from '../../core/features/User/User.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type GetUserQueryVariables = Types.Exact<{ [key: string]: never; }>;


export type GetUserQuery = { __typename?: 'Query', me: { __typename?: 'Me', hasTwoFactorEnabled: boolean, permissions: { __typename?: 'MePermissions', adminPanel: boolean, superUser: boolean, createWorkspace: boolean }, features: Array<{ __typename?: 'FeatureFlag', code: string, config: any }>, user?: { __typename?: 'User', email: string, id: string, firstName?: string | null, lastName?: string | null, displayName: string, language: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null } };

export type AccountPageQueryVariables = Types.Exact<{ [key: string]: never; }>;


export type AccountPageQuery = { __typename?: 'Query', me: { __typename?: 'Me', hasTwoFactorEnabled: boolean, user?: { __typename?: 'User', firstName?: string | null, lastName?: string | null, dateJoined: any, displayName: string, id: string, email: string, language: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null }, pendingWorkspaceInvitations: { __typename?: 'WorkspaceInvitationPage', totalItems: number, items: Array<{ __typename?: 'WorkspaceInvitation', id: string, status: Types.WorkspaceInvitationStatus, role: Types.WorkspaceMembershipRole, createdAt: any, invitedBy?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null, workspace: { __typename?: 'Workspace', slug: string, name: string } }> } };

export type RegisterPageQueryVariables = Types.Exact<{ [key: string]: never; }>;


export type RegisterPageQuery = { __typename?: 'Query', config: { __typename?: 'Config', passwordRequirements?: Array<string> | null } };


export const GetUserDocument = gql`
    query GetUser {
  me {
    hasTwoFactorEnabled
    permissions {
      adminPanel
      superUser
      createWorkspace
    }
    features {
      code
      config
    }
    user {
      ...UserAvatar_user
      email
      id
      firstName
      lastName
      displayName
      language
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
export const RegisterPageDocument = gql`
    query RegisterPage {
  config {
    passwordRequirements
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