import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import { UserAvatar_UserFragmentDoc } from '../../identity/features/UserAvatar.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type Organization_OrganizationFragment = { __typename?: 'Organization', id: string, name: string, shortName?: string | null, workspaces: { __typename?: 'WorkspacePage', totalItems: number, items: Array<{ __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', code: string }> }> }, permissions: { __typename?: 'OrganizationPermissions', createWorkspace: boolean, archiveWorkspace: boolean, manageMembers: boolean, manageOwners: boolean }, members: { __typename?: 'OrganizationMembershipPage', totalItems: number } };

export type OrganizationQueryVariables = Types.Exact<{
  id: Types.Scalars['UUID']['input'];
}>;


export type OrganizationQuery = { __typename?: 'Query', organization?: { __typename?: 'Organization', id: string, name: string, shortName?: string | null, workspaces: { __typename?: 'WorkspacePage', totalItems: number, items: Array<{ __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', code: string }> }> }, permissions: { __typename?: 'OrganizationPermissions', createWorkspace: boolean, archiveWorkspace: boolean, manageMembers: boolean, manageOwners: boolean }, members: { __typename?: 'OrganizationMembershipPage', totalItems: number } } | null };

export type OrganizationsQueryVariables = Types.Exact<{ [key: string]: never; }>;


export type OrganizationsQuery = { __typename?: 'Query', organizations: Array<{ __typename?: 'Organization', id: string, name: string, workspaces: { __typename?: 'WorkspacePage', items: Array<{ __typename?: 'Workspace', slug: string, name: string }> } }> };

export type OrganizationDataset_LinkFragment = { __typename?: 'DatasetLink', id: string, dataset: { __typename?: 'Dataset', id: string, slug: string, name: string, description?: string | null, updatedAt: any, sharedWithOrganization: boolean, workspace?: { __typename?: 'Workspace', slug: string, name: string } | null, links: { __typename?: 'DatasetLinkPage', items: Array<{ __typename?: 'DatasetLink', workspace: { __typename?: 'Workspace', slug: string, name: string } }> } } };

export type OrganizationDatasetsQueryVariables = Types.Exact<{
  id: Types.Scalars['UUID']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  query?: Types.InputMaybe<Types.Scalars['String']['input']>;
}>;


export type OrganizationDatasetsQuery = { __typename?: 'Query', organization?: { __typename?: 'Organization', id: string, name: string, shortName?: string | null, datasetLinks: { __typename?: 'DatasetLinkPage', totalItems: number, pageNumber: number, totalPages: number, items: Array<{ __typename?: 'DatasetLink', id: string, dataset: { __typename?: 'Dataset', id: string, slug: string, name: string, description?: string | null, updatedAt: any, sharedWithOrganization: boolean, workspace?: { __typename?: 'Workspace', slug: string, name: string } | null, links: { __typename?: 'DatasetLinkPage', items: Array<{ __typename?: 'DatasetLink', workspace: { __typename?: 'Workspace', slug: string, name: string } }> } } }> }, workspaces: { __typename?: 'WorkspacePage', totalItems: number, items: Array<{ __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', code: string }> }> }, permissions: { __typename?: 'OrganizationPermissions', createWorkspace: boolean, archiveWorkspace: boolean, manageMembers: boolean, manageOwners: boolean }, members: { __typename?: 'OrganizationMembershipPage', totalItems: number } } | null };

export type OrganizationWorkspace_WorkspaceFragment = { __typename?: 'Workspace', slug: string, name: string, createdAt: any, updatedAt?: any | null, countries: Array<{ __typename?: 'Country', code: string }>, createdBy: { __typename?: 'User', displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } }, members: { __typename?: 'WorkspaceMembershipPage', totalItems: number }, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, delete: boolean } };

export type OrganizationWorkspacesQueryVariables = Types.Exact<{
  organizationId: Types.Scalars['UUID']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  query?: Types.InputMaybe<Types.Scalars['String']['input']>;
}>;


export type OrganizationWorkspacesQuery = { __typename?: 'Query', organization?: { __typename?: 'Organization', id: string, name: string, shortName?: string | null, workspaces: { __typename?: 'WorkspacePage', totalItems: number, items: Array<{ __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', code: string }> }> }, permissions: { __typename?: 'OrganizationPermissions', createWorkspace: boolean, archiveWorkspace: boolean, manageMembers: boolean, manageOwners: boolean }, members: { __typename?: 'OrganizationMembershipPage', totalItems: number } } | null, workspaces: { __typename?: 'WorkspacePage', totalItems: number, pageNumber: number, totalPages: number, items: Array<{ __typename?: 'Workspace', slug: string, name: string, createdAt: any, updatedAt?: any | null, countries: Array<{ __typename?: 'Country', code: string }>, createdBy: { __typename?: 'User', displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } }, members: { __typename?: 'WorkspaceMembershipPage', totalItems: number }, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, delete: boolean } }> } };

export const Organization_OrganizationFragmentDoc = gql`
    fragment Organization_organization on Organization {
  id
  name
  shortName
  workspaces {
    totalItems
    items {
      slug
      name
      countries {
        code
      }
    }
  }
  permissions {
    createWorkspace
    archiveWorkspace
    manageMembers
    manageOwners
  }
  members {
    totalItems
  }
}
    `;
export const OrganizationDataset_LinkFragmentDoc = gql`
    fragment OrganizationDataset_link on DatasetLink {
  id
  dataset {
    id
    slug
    name
    description
    updatedAt
    sharedWithOrganization
    workspace {
      slug
      name
    }
    links(page: 1, perPage: 50) {
      items {
        workspace {
          slug
          name
        }
      }
    }
  }
}
    `;
export const OrganizationWorkspace_WorkspaceFragmentDoc = gql`
    fragment OrganizationWorkspace_workspace on Workspace {
  slug
  name
  createdAt
  updatedAt
  countries {
    code
  }
  createdBy {
    ...UserAvatar_user
  }
  members {
    totalItems
  }
  permissions {
    manageMembers
    delete
  }
}
    ${UserAvatar_UserFragmentDoc}`;
export const OrganizationDocument = gql`
    query Organization($id: UUID!) {
  organization(id: $id) {
    ...Organization_organization
  }
}
    ${Organization_OrganizationFragmentDoc}`;

/**
 * __useOrganizationQuery__
 *
 * To run a query within a React component, call `useOrganizationQuery` and pass it any options that fit your needs.
 * When your component renders, `useOrganizationQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useOrganizationQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useOrganizationQuery(baseOptions: Apollo.QueryHookOptions<OrganizationQuery, OrganizationQueryVariables> & ({ variables: OrganizationQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<OrganizationQuery, OrganizationQueryVariables>(OrganizationDocument, options);
      }
export function useOrganizationLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<OrganizationQuery, OrganizationQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<OrganizationQuery, OrganizationQueryVariables>(OrganizationDocument, options);
        }
export function useOrganizationSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<OrganizationQuery, OrganizationQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<OrganizationQuery, OrganizationQueryVariables>(OrganizationDocument, options);
        }
export type OrganizationQueryHookResult = ReturnType<typeof useOrganizationQuery>;
export type OrganizationLazyQueryHookResult = ReturnType<typeof useOrganizationLazyQuery>;
export type OrganizationSuspenseQueryHookResult = ReturnType<typeof useOrganizationSuspenseQuery>;
export type OrganizationQueryResult = Apollo.QueryResult<OrganizationQuery, OrganizationQueryVariables>;
export const OrganizationsDocument = gql`
    query Organizations {
  organizations {
    id
    name
    workspaces {
      items {
        slug
        name
      }
    }
  }
}
    `;

/**
 * __useOrganizationsQuery__
 *
 * To run a query within a React component, call `useOrganizationsQuery` and pass it any options that fit your needs.
 * When your component renders, `useOrganizationsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useOrganizationsQuery({
 *   variables: {
 *   },
 * });
 */
export function useOrganizationsQuery(baseOptions?: Apollo.QueryHookOptions<OrganizationsQuery, OrganizationsQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<OrganizationsQuery, OrganizationsQueryVariables>(OrganizationsDocument, options);
      }
export function useOrganizationsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<OrganizationsQuery, OrganizationsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<OrganizationsQuery, OrganizationsQueryVariables>(OrganizationsDocument, options);
        }
export function useOrganizationsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<OrganizationsQuery, OrganizationsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<OrganizationsQuery, OrganizationsQueryVariables>(OrganizationsDocument, options);
        }
export type OrganizationsQueryHookResult = ReturnType<typeof useOrganizationsQuery>;
export type OrganizationsLazyQueryHookResult = ReturnType<typeof useOrganizationsLazyQuery>;
export type OrganizationsSuspenseQueryHookResult = ReturnType<typeof useOrganizationsSuspenseQuery>;
export type OrganizationsQueryResult = Apollo.QueryResult<OrganizationsQuery, OrganizationsQueryVariables>;
export const OrganizationDatasetsDocument = gql`
    query OrganizationDatasets($id: UUID!, $page: Int = 1, $perPage: Int = 10, $query: String) {
  organization(id: $id) {
    ...Organization_organization
    datasetLinks(page: $page, perPage: $perPage, query: $query) {
      totalItems
      pageNumber
      totalPages
      items {
        ...OrganizationDataset_link
      }
    }
  }
}
    ${Organization_OrganizationFragmentDoc}
${OrganizationDataset_LinkFragmentDoc}`;

/**
 * __useOrganizationDatasetsQuery__
 *
 * To run a query within a React component, call `useOrganizationDatasetsQuery` and pass it any options that fit your needs.
 * When your component renders, `useOrganizationDatasetsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useOrganizationDatasetsQuery({
 *   variables: {
 *      id: // value for 'id'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *      query: // value for 'query'
 *   },
 * });
 */
export function useOrganizationDatasetsQuery(baseOptions: Apollo.QueryHookOptions<OrganizationDatasetsQuery, OrganizationDatasetsQueryVariables> & ({ variables: OrganizationDatasetsQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<OrganizationDatasetsQuery, OrganizationDatasetsQueryVariables>(OrganizationDatasetsDocument, options);
      }
export function useOrganizationDatasetsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<OrganizationDatasetsQuery, OrganizationDatasetsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<OrganizationDatasetsQuery, OrganizationDatasetsQueryVariables>(OrganizationDatasetsDocument, options);
        }
export function useOrganizationDatasetsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<OrganizationDatasetsQuery, OrganizationDatasetsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<OrganizationDatasetsQuery, OrganizationDatasetsQueryVariables>(OrganizationDatasetsDocument, options);
        }
export type OrganizationDatasetsQueryHookResult = ReturnType<typeof useOrganizationDatasetsQuery>;
export type OrganizationDatasetsLazyQueryHookResult = ReturnType<typeof useOrganizationDatasetsLazyQuery>;
export type OrganizationDatasetsSuspenseQueryHookResult = ReturnType<typeof useOrganizationDatasetsSuspenseQuery>;
export type OrganizationDatasetsQueryResult = Apollo.QueryResult<OrganizationDatasetsQuery, OrganizationDatasetsQueryVariables>;
export const OrganizationWorkspacesDocument = gql`
    query OrganizationWorkspaces($organizationId: UUID!, $page: Int = 1, $perPage: Int = 10, $query: String) {
  organization(id: $organizationId) {
    ...Organization_organization
  }
  workspaces(
    organizationId: $organizationId
    page: $page
    perPage: $perPage
    query: $query
  ) {
    totalItems
    pageNumber
    totalPages
    items {
      ...OrganizationWorkspace_workspace
    }
  }
}
    ${Organization_OrganizationFragmentDoc}
${OrganizationWorkspace_WorkspaceFragmentDoc}`;

/**
 * __useOrganizationWorkspacesQuery__
 *
 * To run a query within a React component, call `useOrganizationWorkspacesQuery` and pass it any options that fit your needs.
 * When your component renders, `useOrganizationWorkspacesQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useOrganizationWorkspacesQuery({
 *   variables: {
 *      organizationId: // value for 'organizationId'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *      query: // value for 'query'
 *   },
 * });
 */
export function useOrganizationWorkspacesQuery(baseOptions: Apollo.QueryHookOptions<OrganizationWorkspacesQuery, OrganizationWorkspacesQueryVariables> & ({ variables: OrganizationWorkspacesQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<OrganizationWorkspacesQuery, OrganizationWorkspacesQueryVariables>(OrganizationWorkspacesDocument, options);
      }
export function useOrganizationWorkspacesLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<OrganizationWorkspacesQuery, OrganizationWorkspacesQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<OrganizationWorkspacesQuery, OrganizationWorkspacesQueryVariables>(OrganizationWorkspacesDocument, options);
        }
export function useOrganizationWorkspacesSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<OrganizationWorkspacesQuery, OrganizationWorkspacesQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<OrganizationWorkspacesQuery, OrganizationWorkspacesQueryVariables>(OrganizationWorkspacesDocument, options);
        }
export type OrganizationWorkspacesQueryHookResult = ReturnType<typeof useOrganizationWorkspacesQuery>;
export type OrganizationWorkspacesLazyQueryHookResult = ReturnType<typeof useOrganizationWorkspacesLazyQuery>;
export type OrganizationWorkspacesSuspenseQueryHookResult = ReturnType<typeof useOrganizationWorkspacesSuspenseQuery>;
export type OrganizationWorkspacesQueryResult = Apollo.QueryResult<OrganizationWorkspacesQuery, OrganizationWorkspacesQueryVariables>;