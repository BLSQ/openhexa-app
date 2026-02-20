import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type WebappPlayQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  webappSlug: Types.Scalars['String']['input'];
}>;


export type WebappPlayQuery = { __typename?: 'Query', webapp?: { __typename?: 'Webapp', id: string, slug: string, name: string, url: string, type: Types.WebappType } | null };


export const WebappPlayDocument = gql`
    query WebappPlay($workspaceSlug: String!, $webappSlug: String!) {
  webapp(workspaceSlug: $workspaceSlug, slug: $webappSlug) {
    id
    slug
    name
    url
    type
  }
}
    `;

/**
 * __useWebappPlayQuery__
 *
 * To run a query within a React component, call `useWebappPlayQuery` and pass it any options that fit your needs.
 * When your component renders, `useWebappPlayQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWebappPlayQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      webappSlug: // value for 'webappSlug'
 *   },
 * });
 */
export function useWebappPlayQuery(baseOptions: Apollo.QueryHookOptions<WebappPlayQuery, WebappPlayQueryVariables> & ({ variables: WebappPlayQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WebappPlayQuery, WebappPlayQueryVariables>(WebappPlayDocument, options);
      }
export function useWebappPlayLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WebappPlayQuery, WebappPlayQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WebappPlayQuery, WebappPlayQueryVariables>(WebappPlayDocument, options);
        }
export function useWebappPlaySuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WebappPlayQuery, WebappPlayQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WebappPlayQuery, WebappPlayQueryVariables>(WebappPlayDocument, options);
        }
export type WebappPlayQueryHookResult = ReturnType<typeof useWebappPlayQuery>;
export type WebappPlayLazyQueryHookResult = ReturnType<typeof useWebappPlayLazyQuery>;
export type WebappPlaySuspenseQueryHookResult = ReturnType<typeof useWebappPlaySuspenseQuery>;
export type WebappPlayQueryResult = Apollo.QueryResult<WebappPlayQuery, WebappPlayQueryVariables>;