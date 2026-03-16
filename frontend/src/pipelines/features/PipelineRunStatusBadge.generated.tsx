import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
export type PipelineRunStatusBadge_RunFragment = { __typename?: 'PipelineRun', id: string, status: Types.PipelineRunStatus, hasErrorMessages: boolean };

export const PipelineRunStatusBadge_RunFragmentDoc = gql`
    fragment PipelineRunStatusBadge_run on PipelineRun {
  id
  status
  hasErrorMessages
}
    `;