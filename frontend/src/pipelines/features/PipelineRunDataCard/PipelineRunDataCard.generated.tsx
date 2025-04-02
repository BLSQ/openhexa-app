import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { PipelineRunReadonlyForm_DagFragmentDoc, PipelineRunReadonlyForm_DagRunFragmentDoc } from '../PipelineRunForm/PipelineRunReadonlyForm.generated';
import { PipelineRunOutputEntry_OutputFragmentDoc } from '../PipelineRunOutputEntry.generated';
import { UserProperty_UserFragmentDoc } from '../../../core/components/DataCard/UserProperty.generated';
import { RunMessages_DagRunFragmentDoc } from '../RunMessages/RunMessages.generated';
import { RunLogs_DagRunFragmentDoc } from '../RunLogs/RunLogs.generated';
import { PipelineRunFavoriteTrigger_RunFragmentDoc } from '../PipelineRunFavoriteTrigger/PipelineRunFavoriteTrigger.generated';
export type PipelineRunDataCard_DagFragment = { __typename?: 'DAG', id: string, externalId: string, label: string, formCode?: string | null };

export type PipelineRunDataCard_DagRunFragment = { __typename?: 'DAGRun', id: string, label?: string | null, externalId?: string | null, externalUrl?: any | null, executionDate?: any | null, triggerMode?: Types.DagRunTrigger | null, status: Types.DagRunStatus, config?: any | null, duration?: number | null, progress: number, logs?: string | null, isFavorite: boolean, outputs: Array<{ __typename?: 'DAGRunOutput', title: string, uri: string }>, user?: { __typename?: 'User', displayName: string, id: string, email: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null, messages: Array<{ __typename: 'DAGRunMessage', message: string, timestamp?: any | null, priority: string }> };

export const PipelineRunDataCard_DagFragmentDoc = gql`
    fragment PipelineRunDataCard_dag on DAG {
  id
  externalId
  label
  ...PipelineRunReadonlyForm_dag
}
    ${PipelineRunReadonlyForm_DagFragmentDoc}`;
export const PipelineRunDataCard_DagRunFragmentDoc = gql`
    fragment PipelineRunDataCard_dagRun on DAGRun {
  id
  label
  externalId
  externalUrl
  executionDate
  triggerMode
  status
  config
  duration
  outputs {
    ...PipelineRunOutputEntry_output
  }
  user {
    displayName
    ...UserProperty_user
  }
  progress
  messages {
    __typename
  }
  ...RunMessages_dagRun
  ...RunLogs_dagRun
  ...PipelineRunReadonlyForm_dagRun
  ...PipelineRunFavoriteTrigger_run
}
    ${PipelineRunOutputEntry_OutputFragmentDoc}
${UserProperty_UserFragmentDoc}
${RunMessages_DagRunFragmentDoc}
${RunLogs_DagRunFragmentDoc}
${PipelineRunReadonlyForm_DagRunFragmentDoc}
${PipelineRunFavoriteTrigger_RunFragmentDoc}`;