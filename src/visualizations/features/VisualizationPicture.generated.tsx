import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
export type VisualizationPicture_VisualizationFragment = { __typename?: 'ExternalDashboard', pictureUrl: any };

export const VisualizationPicture_VisualizationFragmentDoc = gql`
    fragment VisualizationPicture_visualization on ExternalDashboard {
  pictureUrl
}
    `;