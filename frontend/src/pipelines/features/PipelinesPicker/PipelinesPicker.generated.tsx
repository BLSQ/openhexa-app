import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type PipelinesPicker_ValueFragment = { __typename?: 'DAG', id: string, externalId: string };

export const PipelinesPicker_ValueFragmentDoc = gql`
    fragment PipelinesPicker_value on DAG {
  id
  externalId
}
    `;