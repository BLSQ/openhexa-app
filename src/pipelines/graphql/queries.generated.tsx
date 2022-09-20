import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
import { CountryBadge_CountryFragmentDoc } from '../../core/features/CountryBadge.generated';
import { Tag_TagFragmentDoc } from '../../core/features/Tag.generated';
import { PipelineRunStatusBadge_DagRunFragmentDoc } from '../features/PipelineRunStatusBadge.generated';
import { UserProperty_UserFragmentDoc } from '../../core/components/DataCard/UserProperty.generated';
import { UserColumn_UserFragmentDoc } from '../../core/components/DataGrid/UserColumn.generated';
import { RunMessages_DagRunFragmentDoc } from '../features/RunMessages/RunMessages.generated';
import { RunLogs_DagRunFragmentDoc } from '../features/RunLogs/RunLogs.generated';
import { PipelineRunForm_DagFragmentDoc } from '../features/PipelineRunForm/PipelineRunForm.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type PipelinesPageQueryVariables = Types.Exact<{ [key: string]: never; }>;


export type PipelinesPageQuery = { __typename?: 'Query', dags: { __typename?: 'DAGPage', totalPages: number, totalItems: number, items: Array<{ __typename?: 'DAG', label: string, id: string, code: string, countries: Array<{ __typename?: 'Country', code: string, name: string, flag: string }>, tags: Array<{ __typename?: 'Tag', id: string, name: string }>, runs: { __typename?: 'DAGRunPage', items: Array<{ __typename?: 'DAGRun', id: string, status: Types.DagRunStatus, executionDate?: any | null }> } }> } };

export type PipelinePageQueryVariables = Types.Exact<{
  id: Types.Scalars['String'];
  page?: Types.InputMaybe<Types.Scalars['Int']>;
}>;


export type PipelinePageQuery = { __typename?: 'Query', dag?: { __typename?: 'DAG', id: string, label: string, code: string, schedule?: string | null, externalUrl?: any | null, countries: Array<{ __typename?: 'Country', code: string, name: string, flag: string }>, tags: Array<{ __typename?: 'Tag', id: string, name: string }>, template: { __typename?: 'DAGTemplate', code: string, description?: string | null, sampleConfig?: any | null }, user?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null, runs: { __typename?: 'DAGRunPage', totalItems: number, totalPages: number, items: Array<{ __typename?: 'DAGRun', id: string, triggerMode?: Types.DagRunTrigger | null, externalId?: string | null, externalUrl?: any | null, status: Types.DagRunStatus, executionDate?: any | null, lastRefreshedAt?: any | null, duration?: number | null, user?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null }> } } | null };

export type PipelineRunPageQueryVariables = Types.Exact<{
  pipelineId: Types.Scalars['String'];
  runId: Types.Scalars['String'];
}>;


export type PipelineRunPageQuery = { __typename?: 'Query', dagRun?: { __typename?: 'DAGRun', id: string, externalId?: string | null, externalUrl?: any | null, executionDate?: any | null, status: Types.DagRunStatus, config?: any | null, logs?: string | null, outputs: Array<{ __typename?: 'DAGRunOutput', title: string, uri: string }>, messages: Array<{ __typename?: 'DAGRunMessage', message: string, timestamp?: any | null, priority: string }> } | null, dag?: { __typename?: 'DAG', id: string, code: string, label: string } | null };

export type PipelineConfigureRunPageQueryVariables = Types.Exact<{
  pipelineId: Types.Scalars['String'];
}>;


export type PipelineConfigureRunPageQuery = { __typename?: 'Query', dag?: { __typename?: 'DAG', id: string, code: string, template: { __typename?: 'DAGTemplate', sampleConfig?: any | null, description?: string | null } } | null };


export const PipelinesPageDocument = gql`
    query PipelinesPage {
  dags {
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
      code
      runs(orderBy: EXECUTION_DATE_DESC, perPage: 1) {
        items {
          id
          status
          executionDate
          ...PipelineRunStatusBadge_dagRun
        }
      }
    }
  }
}
    ${CountryBadge_CountryFragmentDoc}
${Tag_TagFragmentDoc}
${PipelineRunStatusBadge_DagRunFragmentDoc}`;

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
export type PipelinesPageQueryHookResult = ReturnType<typeof usePipelinesPageQuery>;
export type PipelinesPageLazyQueryHookResult = ReturnType<typeof usePipelinesPageLazyQuery>;
export type PipelinesPageQueryResult = Apollo.QueryResult<PipelinesPageQuery, PipelinesPageQueryVariables>;
export const PipelinePageDocument = gql`
    query PipelinePage($id: String!, $page: Int) {
  dag(id: $id) {
    id
    label
    countries {
      ...CountryBadge_country
    }
    tags {
      ...Tag_tag
    }
    code
    schedule
    externalUrl
    template {
      code
      description
      sampleConfig
    }
    schedule
    user {
      ...UserProperty_user
    }
    runs(page: $page, perPage: 15) {
      totalItems
      totalPages
      items {
        id
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
        ...PipelineRunStatusBadge_dagRun
      }
    }
  }
}
    ${CountryBadge_CountryFragmentDoc}
${Tag_TagFragmentDoc}
${UserProperty_UserFragmentDoc}
${UserColumn_UserFragmentDoc}
${PipelineRunStatusBadge_DagRunFragmentDoc}`;

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
 *   },
 * });
 */
export function usePipelinePageQuery(baseOptions: Apollo.QueryHookOptions<PipelinePageQuery, PipelinePageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<PipelinePageQuery, PipelinePageQueryVariables>(PipelinePageDocument, options);
      }
export function usePipelinePageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<PipelinePageQuery, PipelinePageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<PipelinePageQuery, PipelinePageQueryVariables>(PipelinePageDocument, options);
        }
export type PipelinePageQueryHookResult = ReturnType<typeof usePipelinePageQuery>;
export type PipelinePageLazyQueryHookResult = ReturnType<typeof usePipelinePageLazyQuery>;
export type PipelinePageQueryResult = Apollo.QueryResult<PipelinePageQuery, PipelinePageQueryVariables>;
export const PipelineRunPageDocument = gql`
    query PipelineRunPage($pipelineId: String!, $runId: String!) {
  dagRun(id: $runId) {
    id
    externalId
    externalUrl
    executionDate
    status
    config
    outputs {
      title
      uri
    }
    ...RunMessages_dagRun
    ...RunLogs_dagRun
    ...PipelineRunStatusBadge_dagRun
  }
  dag(id: $pipelineId) {
    id
    code
    label
  }
}
    ${RunMessages_DagRunFragmentDoc}
${RunLogs_DagRunFragmentDoc}
${PipelineRunStatusBadge_DagRunFragmentDoc}`;

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
export function usePipelineRunPageQuery(baseOptions: Apollo.QueryHookOptions<PipelineRunPageQuery, PipelineRunPageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<PipelineRunPageQuery, PipelineRunPageQueryVariables>(PipelineRunPageDocument, options);
      }
export function usePipelineRunPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<PipelineRunPageQuery, PipelineRunPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<PipelineRunPageQuery, PipelineRunPageQueryVariables>(PipelineRunPageDocument, options);
        }
export type PipelineRunPageQueryHookResult = ReturnType<typeof usePipelineRunPageQuery>;
export type PipelineRunPageLazyQueryHookResult = ReturnType<typeof usePipelineRunPageLazyQuery>;
export type PipelineRunPageQueryResult = Apollo.QueryResult<PipelineRunPageQuery, PipelineRunPageQueryVariables>;
export const PipelineConfigureRunPageDocument = gql`
    query PipelineConfigureRunPage($pipelineId: String!) {
  dag(id: $pipelineId) {
    id
    code
    template {
      sampleConfig
      description
    }
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
export function usePipelineConfigureRunPageQuery(baseOptions: Apollo.QueryHookOptions<PipelineConfigureRunPageQuery, PipelineConfigureRunPageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<PipelineConfigureRunPageQuery, PipelineConfigureRunPageQueryVariables>(PipelineConfigureRunPageDocument, options);
      }
export function usePipelineConfigureRunPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<PipelineConfigureRunPageQuery, PipelineConfigureRunPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<PipelineConfigureRunPageQuery, PipelineConfigureRunPageQueryVariables>(PipelineConfigureRunPageDocument, options);
        }
export type PipelineConfigureRunPageQueryHookResult = ReturnType<typeof usePipelineConfigureRunPageQuery>;
export type PipelineConfigureRunPageLazyQueryHookResult = ReturnType<typeof usePipelineConfigureRunPageLazyQuery>;
export type PipelineConfigureRunPageQueryResult = Apollo.QueryResult<PipelineConfigureRunPageQuery, PipelineConfigureRunPageQueryVariables>;