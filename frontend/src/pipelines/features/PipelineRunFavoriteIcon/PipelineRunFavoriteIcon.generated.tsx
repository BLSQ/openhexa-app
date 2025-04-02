import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type PipelineRunFavoriteIcon_RunFragment = { __typename?: 'DAGRun', isFavorite: boolean };

export const PipelineRunFavoriteIcon_RunFragmentDoc = gql`
    fragment PipelineRunFavoriteIcon_run on DAGRun {
  isFavorite
}
    `;