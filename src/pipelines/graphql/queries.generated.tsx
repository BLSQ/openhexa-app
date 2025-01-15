import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import { CountryBadge_CountryFragmentDoc } from '../../core/features/CountryBadge.generated';
import { Tag_TagFragmentDoc } from '../../core/features/Tag.generated';
import { UserProperty_UserFragmentDoc } from '../../core/components/DataCard/UserProperty.generated';
import { UserColumn_UserFragmentDoc } from '../../core/components/DataGrid/UserColumn.generated';
import { PipelineRunFavoriteTrigger_RunFragmentDoc } from '../features/PipelineRunFavoriteTrigger/PipelineRunFavoriteTrigger.generated';
import { PipelineRunDataCard_DagRunFragmentDoc, PipelineRunDataCard_DagFragmentDoc } from '../features/PipelineRunDataCard/PipelineRunDataCard.generated';
import { PipelineRunForm_DagFragmentDoc } from '../features/PipelineRunForm/PipelineRunForm.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type PipelinesPageQueryVariables = Types.Exact<{
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type PipelinesPageQuery = { __typename?: 'Query', dags: { __typename?: 'DAGPage', totalPages: number, totalItems: number, items: Array<{ __typename?: 'DAG', label: string, id: string, externalId: string, countries: Array<{ __typename?: 'Country', code: string, name: string }>, tags: Array<{ __typename?: 'Tag', id: string, name: string }>, runs: { __typename?: 'DAGRunPage', items: Array<{ __typename?: 'DAGRun', id: string, status: Types.DagRunStatus, executionDate?: any | null }> } }> } };

export type PipelinePageQueryVariables = Types.Exact<{
  id: Types.Scalars['UUID']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type PipelinePageQuery = { __typename?: 'Query', dag?: { __typename?: 'DAG', id: string, label: string, externalId: string, schedule?: string | null, externalUrl?: any | null, description?: string | null, countries: Array<{ __typename?: 'Country', code: string, name: string }>, tags: Array<{ __typename?: 'Tag', id: string, name: string }>, template: { __typename?: 'DAGTemplate', code: string, description?: string | null, sampleConfig?: any | null }, user?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null, runs: { __typename?: 'DAGRunPage', totalItems: number, totalPages: number, items: Array<{ __typename?: 'DAGRun', id: string, label?: string | null, triggerMode?: Types.DagRunTrigger | null, externalId?: string | null, externalUrl?: any | null, status: Types.DagRunStatus, executionDate?: any | null, lastRefreshedAt?: any | null, duration?: number | null, isFavorite: boolean, user?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null }> } } | null };

export type PipelineRunPageQueryVariables = Types.Exact<{
  pipelineId: Types.Scalars['UUID']['input'];
  runId: Types.Scalars['UUID']['input'];
}>;


export type PipelineRunPageQuery = { __typename?: 'Query', dagRun?: { __typename?: 'DAGRun', id: string, label?: string | null, triggerMode?: Types.DagRunTrigger | null, externalId?: string | null, externalUrl?: any | null, executionDate?: any | null, status: Types.DagRunStatus, config?: any | null, duration?: number | null, progress: number, logs?: string | null, isFavorite: boolean, user?: { __typename?: 'User', displayName: string, id: string, email: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null, outputs: Array<{ __typename?: 'DAGRunOutput', title: string, uri: string }>, messages: Array<{ __typename: 'DAGRunMessage', message: string, timestamp?: any | null, priority: string }> } | null, dag?: { __typename?: 'DAG', id: string, externalId: string, label: string, formCode?: string | null } | null };

export type PipelineConfigureRunPageQueryVariables = Types.Exact<{
  pipelineId: Types.Scalars['UUID']['input'];
}>;


export type PipelineConfigureRunPageQuery = { __typename?: 'Query', dag?: { __typename?: 'DAG', id: string, label: string, externalId: string, description?: string | null, formCode?: string | null, template: { __typename?: 'DAGTemplate', sampleConfig?: any | null, description?: string | null } } | null };


export const PipelinesPageDocument = gql`
    query PipelinesPage($page: Int, $perPage: Int = 15) {
  dags(page: $page, perPage: $perPage) {
    totalPages
    totalItems
    items {
      label
      countries {
        ...CountryBadge_country
      }
      tags {
        ...Tag_tag
      }
      id
      externalId
      runs(orderBy: EXECUTION_DATE_DESC, perPage: 1) {
        items {
          id
          status
          executionDate
        }
      }
    }
  }
}
    ${CountryBadge_CountryFragmentDoc}
${Tag_TagFragmentDoc}`;

/**
 * __usePipelinesPageQuery__
 *
 * To run a query within a React component, call `usePipelinesPageQuery` and pass it any options that fit your needs.
 * When your component renders, `usePipelinesPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = usePipelinesPageQuery({
 *   variables: {
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function usePipelinesPageQuery(baseOptions?: Apollo.QueryHookOptions<PipelinesPageQuery, PipelinesPageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<PipelinesPageQuery, PipelinesPageQueryVariables>(PipelinesPageDocument, options);
      }
export function usePipelinesPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<PipelinesPageQuery, PipelinesPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<PipelinesPageQuery, PipelinesPageQueryVariables>(PipelinesPageDocument, options);
        }
export function usePipelinesPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<PipelinesPageQuery, PipelinesPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<PipelinesPageQuery, PipelinesPageQueryVariables>(PipelinesPageDocument, options);
        }
export type PipelinesPageQueryHookResult = ReturnType<typeof usePipelinesPageQuery>;
export type PipelinesPageLazyQueryHookResult = ReturnType<typeof usePipelinesPageLazyQuery>;
export type PipelinesPageSuspenseQueryHookResult = ReturnType<typeof usePipelinesPageSuspenseQuery>;
export type PipelinesPageQueryResult = Apollo.QueryResult<PipelinesPageQuery, PipelinesPageQueryVariables>;
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
export const PipelineRunPageDocument = gql`
    query PipelineRunPage($pipelineId: UUID!, $runId: UUID!) {
  dagRun(id: $runId) {
    id
    label
    triggerMode
    user {
      displayName
    }
    ...PipelineRunDataCard_dagRun
  }
  dag(id: $pipelineId) {
    id
    externalId
    label
    ...PipelineRunDataCard_dag
  }
}
    ${PipelineRunDataCard_DagRunFragmentDoc}
${PipelineRunDataCard_DagFragmentDoc}`;

/**
 * __usePipelineRunPageQuery__
 *
 * To run a query within a React component, call `usePipelineRunPageQuery` and pass it any options that fit your needs.
 * When your component renders, `usePipelineRunPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = usePipelineRunPageQuery({
 *   variables: {
 *      pipelineId: // value for 'pipelineId'
 *      runId: // value for 'runId'
 *   },
 * });
 */
export function usePipelineRunPageQuery(baseOptions: Apollo.QueryHookOptions<PipelineRunPageQuery, PipelineRunPageQueryVariables> & ({ variables: PipelineRunPageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<PipelineRunPageQuery, PipelineRunPageQueryVariables>(PipelineRunPageDocument, options);
      }
export function usePipelineRunPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<PipelineRunPageQuery, PipelineRunPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<PipelineRunPageQuery, PipelineRunPageQueryVariables>(PipelineRunPageDocument, options);
        }
export function usePipelineRunPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<PipelineRunPageQuery, PipelineRunPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<PipelineRunPageQuery, PipelineRunPageQueryVariables>(PipelineRunPageDocument, options);
        }
export type PipelineRunPageQueryHookResult = ReturnType<typeof usePipelineRunPageQuery>;
export type PipelineRunPageLazyQueryHookResult = ReturnType<typeof usePipelineRunPageLazyQuery>;
export type PipelineRunPageSuspenseQueryHookResult = ReturnType<typeof usePipelineRunPageSuspenseQuery>;
export type PipelineRunPageQueryResult = Apollo.QueryResult<PipelineRunPageQuery, PipelineRunPageQueryVariables>;
export const PipelineConfigureRunPageDocument = gql`
    query PipelineConfigureRunPage($pipelineId: UUID!) {
  dag(id: $pipelineId) {
    id
    label
    externalId
    template {
      sampleConfig
      description
    }
    description
    ...PipelineRunForm_dag
  }
}
    ${PipelineRunForm_DagFragmentDoc}`;

/**
 * __usePipelineConfigureRunPageQuery__
 *
 * To run a query within a React component, call `usePipelineConfigureRunPageQuery` and pass it any options that fit your needs.
 * When your component renders, `usePipelineConfigureRunPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = usePipelineConfigureRunPageQuery({
 *   variables: {
 *      pipelineId: // value for 'pipelineId'
 *   },
 * });
 */
export function usePipelineConfigureRunPageQuery(baseOptions: Apollo.QueryHookOptions<PipelineConfigureRunPageQuery, PipelineConfigureRunPageQueryVariables> & ({ variables: PipelineConfigureRunPageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<PipelineConfigureRunPageQuery, PipelineConfigureRunPageQueryVariables>(PipelineConfigureRunPageDocument, options);
      }
export function usePipelineConfigureRunPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<PipelineConfigureRunPageQuery, PipelineConfigureRunPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<PipelineConfigureRunPageQuery, PipelineConfigureRunPageQueryVariables>(PipelineConfigureRunPageDocument, options);
        }
export function usePipelineConfigureRunPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<PipelineConfigureRunPageQuery, PipelineConfigureRunPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<PipelineConfigureRunPageQuery, PipelineConfigureRunPageQueryVariables>(PipelineConfigureRunPageDocument, options);
        }
export type PipelineConfigureRunPageQueryHookResult = ReturnType<typeof usePipelineConfigureRunPageQuery>;
export type PipelineConfigureRunPageLazyQueryHookResult = ReturnType<typeof usePipelineConfigureRunPageLazyQuery>;
export type PipelineConfigureRunPageSuspenseQueryHookResult = ReturnType<typeof usePipelineConfigureRunPageSuspenseQuery>;
export type PipelineConfigureRunPageQueryResult = Apollo.QueryResult<PipelineConfigureRunPageQuery, PipelineConfigureRunPageQueryVariables>;