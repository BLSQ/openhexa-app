import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type PublicWebappQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  webappSlug: Types.Scalars['String']['input'];
}>;


export type PublicWebappQuery = { __typename?: 'Query', publicWebapp?: { __typename?: 'Webapp', id: string, slug: string, name: string, url: string, type: Types.WebappType } | null };


export const PublicWebappDocument = gql`
    query PublicWebapp($workspaceSlug: String!, $webappSlug: String!) {
  publicWebapp(workspaceSlug: $workspaceSlug, slug: $webappSlug) {
    id
    slug
    name
    url
    type
  }
}
    `;

/**
 * __usePublicWebappQuery__
 *
 * To run a query within a React component, call `usePublicWebappQuery` and pass it any options that fit your needs.
 * When your component renders, `usePublicWebappQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = usePublicWebappQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      webappSlug: // value for 'webappSlug'
 *   },
 * });
 */
export function usePublicWebappQuery(baseOptions: Apollo.QueryHookOptions<PublicWebappQuery, PublicWebappQueryVariables> & ({ variables: PublicWebappQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<PublicWebappQuery, PublicWebappQueryVariables>(PublicWebappDocument, options);
      }
export function usePublicWebappLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<PublicWebappQuery, PublicWebappQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<PublicWebappQuery, PublicWebappQueryVariables>(PublicWebappDocument, options);
        }
export function usePublicWebappSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<PublicWebappQuery, PublicWebappQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<PublicWebappQuery, PublicWebappQueryVariables>(PublicWebappDocument, options);
        }
export type PublicWebappQueryHookResult = ReturnType<typeof usePublicWebappQuery>;
export type PublicWebappLazyQueryHookResult = ReturnType<typeof usePublicWebappLazyQuery>;
export type PublicWebappSuspenseQueryHookResult = ReturnType<typeof usePublicWebappSuspenseQuery>;
export type PublicWebappQueryResult = Apollo.QueryResult<PublicWebappQuery, PublicWebappQueryVariables>;