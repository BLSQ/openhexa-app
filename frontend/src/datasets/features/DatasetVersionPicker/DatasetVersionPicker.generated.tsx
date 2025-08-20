import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type DatasetVersionPicker_VersionFragment = { __typename?: 'DatasetVersion', id: string, name: string, createdAt: any };

export type DatasetVersionPicker_DatasetFragment = { __typename?: 'Dataset', id: string };

export const DatasetVersionPicker_VersionFragmentDoc = gql`
    fragment DatasetVersionPicker_version on DatasetVersion {
  id
  name
  createdAt
}
    `;
export const DatasetVersionPicker_DatasetFragmentDoc = gql`
    fragment DatasetVersionPicker_dataset on Dataset {
  id
}
    `;