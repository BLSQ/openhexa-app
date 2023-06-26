import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
import { VisualizationPicture_VisualizationFragmentDoc } from '../features/VisualizationPicture.generated';
import { CountryBadge_CountryFragmentDoc } from '../../core/features/CountryBadge.generated';
import { Tag_TagFragmentDoc } from '../../core/features/Tag.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type VisualizationsPageQueryVariables = Types.Exact<{
  page?: Types.InputMaybe<Types.Scalars['Int']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']>;
}>;


export type VisualizationsPageQuery = { __typename?: 'Query', externalDashboards: { __typename?: 'ExternalDashboardPage', totalPages: number, totalItems: number, items: Array<{ __typename?: 'ExternalDashboard', id: string, name: string, url: any, description?: string | null, createdAt: any, updatedAt: any, pictureUrl: any, countries: Array<{ __typename?: 'Country', code: string, name: string, flag: string }>, tags: Array<{ __typename?: 'Tag', id: string, name: string }> }> } };

export type VisualizationQueryVariables = Types.Exact<{
  id: Types.Scalars['UUID'];
}>;


export type VisualizationQuery = { __typename?: 'Query', externalDashboard?: { __typename?: 'ExternalDashboard', id: string, name: string, url: any, description?: string | null, createdAt: any, updatedAt: any, pictureUrl: any, countries: Array<{ __typename?: 'Country', code: string, name: string, flag: string }>, tags: Array<{ __typename?: 'Tag', id: string, name: string }> } | null };


export const VisualizationsPageDocument = gql`
    query VisualizationsPage($page: Int, $perPage: Int = 15) {
  externalDashboards(page: $page, perPage: $perPage) {
    totalPages
    totalItems
    items {
      id
      name
      url
      description
      ...VisualizationPicture_visualization
      createdAt
      updatedAt
      countries {
        ...CountryBadge_country
      }
      tags {
        ...Tag_tag
      }
    }
  }
}
    ${VisualizationPicture_VisualizationFragmentDoc}
${CountryBadge_CountryFragmentDoc}
${Tag_TagFragmentDoc}`;

/**
 * __useVisualizationsPageQuery__
 *
 * To run a query within a React component, call `useVisualizationsPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useVisualizationsPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useVisualizationsPageQuery({
 *   variables: {
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useVisualizationsPageQuery(baseOptions?: Apollo.QueryHookOptions<VisualizationsPageQuery, VisualizationsPageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<VisualizationsPageQuery, VisualizationsPageQueryVariables>(VisualizationsPageDocument, options);
      }
export function useVisualizationsPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<VisualizationsPageQuery, VisualizationsPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<VisualizationsPageQuery, VisualizationsPageQueryVariables>(VisualizationsPageDocument, options);
        }
export type VisualizationsPageQueryHookResult = ReturnType<typeof useVisualizationsPageQuery>;
export type VisualizationsPageLazyQueryHookResult = ReturnType<typeof useVisualizationsPageLazyQuery>;
export type VisualizationsPageQueryResult = Apollo.QueryResult<VisualizationsPageQuery, VisualizationsPageQueryVariables>;
export const VisualizationDocument = gql`
    query Visualization($id: UUID!) {
  externalDashboard(id: $id) {
    id
    name
    url
    description
    ...VisualizationPicture_visualization
    createdAt
    updatedAt
    countries {
      ...CountryBadge_country
    }
    tags {
      ...Tag_tag
    }
  }
}
    ${VisualizationPicture_VisualizationFragmentDoc}
${CountryBadge_CountryFragmentDoc}
${Tag_TagFragmentDoc}`;

/**
 * __useVisualizationQuery__
 *
 * To run a query within a React component, call `useVisualizationQuery` and pass it any options that fit your needs.
 * When your component renders, `useVisualizationQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useVisualizationQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useVisualizationQuery(baseOptions: Apollo.QueryHookOptions<VisualizationQuery, VisualizationQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<VisualizationQuery, VisualizationQueryVariables>(VisualizationDocument, options);
      }
export function useVisualizationLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<VisualizationQuery, VisualizationQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<VisualizationQuery, VisualizationQueryVariables>(VisualizationDocument, options);
        }
export type VisualizationQueryHookResult = ReturnType<typeof useVisualizationQuery>;
export type VisualizationLazyQueryHookResult = ReturnType<typeof useVisualizationLazyQuery>;
export type VisualizationQueryResult = Apollo.QueryResult<VisualizationQuery, VisualizationQueryVariables>;