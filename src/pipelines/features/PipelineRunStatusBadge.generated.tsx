import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import { UsePipelineRunPoller_RunFragmentDoc } from '../hooks/usePipelineRunPoller/usePipelineRunPoller.generated';
export type PipelineRunStatusBadge_RunFragment = { __typename?: 'PipelineRun', id: string, status: Types.PipelineRunStatus };

export const PipelineRunStatusBadge_RunFragmentDoc = gql`
    fragment PipelineRunStatusBadge_run on PipelineRun {
  id
  status
  ...usePipelineRunPoller_run
}
    ${UsePipelineRunPoller_RunFragmentDoc}`;