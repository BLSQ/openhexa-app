import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type DeleteDatasetLinkTrigger_DatasetLinkFragment = { __typename?: 'DatasetLink', id: string, dataset: { __typename?: 'Dataset', name: string, id: string }, workspace: { __typename?: 'Workspace', slug: string }, permissions: { __typename?: 'DatasetLinkPermissions', delete: boolean } };

export const DeleteDatasetLinkTrigger_DatasetLinkFragmentDoc = gql`
    fragment DeleteDatasetLinkTrigger_datasetLink on DatasetLink {
  id
  dataset {
    name
    id
  }
  workspace {
    slug
  }
  permissions {
    delete
  }
}
    `;