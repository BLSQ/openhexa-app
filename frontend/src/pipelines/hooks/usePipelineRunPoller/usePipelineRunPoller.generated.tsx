import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type UsePipelineRunPoller_RunFragment = { __typename?: 'PipelineRun', id: string, status: Types.PipelineRunStatus };

export const UsePipelineRunPoller_RunFragmentDoc = gql`
    fragment usePipelineRunPoller_run on PipelineRun {
  id
  status
}
    `;