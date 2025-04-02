import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
export type PipelineRunOutputEntry_OutputFragment = { __typename?: 'DAGRunOutput', title: string, uri: string };

export const PipelineRunOutputEntry_OutputFragmentDoc = gql`
    fragment PipelineRunOutputEntry_output on DAGRunOutput {
  title
  uri
}
    `;