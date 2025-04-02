import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type UploadDatasetVersionDialog_DatasetLinkFragment = { __typename?: 'DatasetLink', id: string, dataset: { __typename?: 'Dataset', id: string, name: string, slug: string, workspace?: { __typename?: 'Workspace', slug: string } | null }, workspace: { __typename?: 'Workspace', slug: string } };

export const UploadDatasetVersionDialog_DatasetLinkFragmentDoc = gql`
    fragment UploadDatasetVersionDialog_datasetLink on DatasetLink {
  id
  dataset {
    id
    name
    slug
    workspace {
      slug
    }
  }
  workspace {
    slug
  }
}
    `;