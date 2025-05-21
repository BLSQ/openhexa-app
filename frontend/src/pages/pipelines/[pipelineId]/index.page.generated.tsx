import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { CountryBadge_CountryFragmentDoc } from '../../../core/features/CountryBadge.generated';
import { Tag_TagFragmentDoc } from '../../../core/features/Tag.generated';
import { UserProperty_UserFragmentDoc } from '../../../core/components/DataCard/UserProperty.generated';
import { UserColumn_UserFragmentDoc } from '../../../core/components/DataGrid/UserColumn.generated';
import { PipelineRunFavoriteTrigger_RunFragmentDoc } from '../../../pipelines/features/PipelineRunFavoriteTrigger/PipelineRunFavoriteTrigger.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type PipelinePageQueryVariables = Types.Exact<{
  id: Types.Scalars['UUID']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type PipelinePageQuery = { __typename?: 'Query', dag?: { __typename?: 'DAG', id: string, label: string, externalId: string, schedule?: string | null, externalUrl?: any | null, description?: string | null, countries: Array<{ __typename?: 'Country', code: string, name: string }>, tags: Array<{ __typename?: 'Tag', id: string, name: string }>, template: { __typename?: 'DAGTemplate', code: string, description?: string | null, sampleConfig?: any | null }, user?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null, runs: { __typename?: 'DAGRunPage', totalItems: number, totalPages: number, items: Array<{ __typename?: 'DAGRun', id: string, label?: string | null, triggerMode?: Types.DagRunTrigger | null, externalId?: string | null, externalUrl?: any | null, status: Types.DagRunStatus, executionDate?: any | null, lastRefreshedAt?: any | null, duration?: number | null, isFavorite: boolean, user?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null }> } } | null };


export const PipelinePageDocument = gql`
    query PipelinePage($id: UUID!, $page: Int, $perPage: Int) {
  dag(id: $id) {
    id
    label
    countries {
      ...CountryBadge_country
    }
    tags {
      ...Tag_tag
    }
    externalId
    schedule
    externalUrl
    template {
      code
      description
      sampleConfig
    }
    description
    schedule
    user {
      ...UserProperty_user
    }
    runs(page: $page, perPage: $perPage) {
      totalItems
      totalPages
      items {
        id
        label
        triggerMode
        externalId
        externalUrl
        user {
          ...UserColumn_user
        }
        status
        executionDate
        lastRefreshedAt
        duration
        ...PipelineRunFavoriteTrigger_run
      }
    }
  }
}
    ${CountryBadge_CountryFragmentDoc}
${Tag_TagFragmentDoc}
${UserProperty_UserFragmentDoc}
${UserColumn_UserFragmentDoc}
${PipelineRunFavoriteTrigger_RunFragmentDoc}`;

/**
 * __usePipelinePageQuery__
 *
 * To run a query within a React component, call `usePipelinePageQuery` and pass it any options that fit your needs.
 * When your component renders, `usePipelinePageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = usePipelinePageQuery({
 *   variables: {
 *      id: // value for 'id'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function usePipelinePageQuery(baseOptions: Apollo.QueryHookOptions<PipelinePageQuery, PipelinePageQueryVariables> & ({ variables: PipelinePageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<PipelinePageQuery, PipelinePageQueryVariables>(PipelinePageDocument, options);
      }
export function usePipelinePageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<PipelinePageQuery, PipelinePageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<PipelinePageQuery, PipelinePageQueryVariables>(PipelinePageDocument, options);
        }
export function usePipelinePageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<PipelinePageQuery, PipelinePageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<PipelinePageQuery, PipelinePageQueryVariables>(PipelinePageDocument, options);
        }
export type PipelinePageQueryHookResult = ReturnType<typeof usePipelinePageQuery>;
export type PipelinePageLazyQueryHookResult = ReturnType<typeof usePipelinePageLazyQuery>;
export type PipelinePageSuspenseQueryHookResult = ReturnType<typeof usePipelinePageSuspenseQuery>;
export type PipelinePageQueryResult = Apollo.QueryResult<PipelinePageQuery, PipelinePageQueryVariables>;