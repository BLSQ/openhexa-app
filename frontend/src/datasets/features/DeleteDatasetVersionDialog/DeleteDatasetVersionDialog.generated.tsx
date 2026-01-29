import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type DeleteDatasetVersionDialog_VersionFragment = { __typename?: 'DatasetVersion', id: string, name: string, dataset: { __typename?: 'Dataset', slug: string }, permissions: { __typename?: 'DatasetVersionPermissions', delete: boolean } };

export const DeleteDatasetVersionDialog_VersionFragmentDoc = gql`
    fragment DeleteDatasetVersionDialog_version on DatasetVersion {
  id
  name
  dataset {
    slug
  }
  permissions {
    delete
  }
}
    `;