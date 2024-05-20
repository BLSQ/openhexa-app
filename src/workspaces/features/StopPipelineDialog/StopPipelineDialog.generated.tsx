import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type StopPipelineDialog_RunFragment = { __typename?: 'PipelineRun', id: string };

export type StopPipelineDialog_PipelineFragment = { __typename?: 'Pipeline', code: string };

export const StopPipelineDialog_RunFragmentDoc = gql`
    fragment StopPipelineDialog_run on PipelineRun {
  id
}
    `;
export const StopPipelineDialog_PipelineFragmentDoc = gql`
    fragment StopPipelineDialog_pipeline on Pipeline {
  code
}
    `;