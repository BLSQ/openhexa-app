import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type DeleteDatasetTrigger_DatasetFragment = { __typename?: 'Dataset', id: string, name: string, workspace?: { __typename?: 'Workspace', slug: string } | null, permissions: { __typename?: 'DatasetPermissions', delete: boolean } };

export const DeleteDatasetTrigger_DatasetFragmentDoc = gql`
    fragment DeleteDatasetTrigger_dataset on Dataset {
  id
  name
  workspace {
    slug
  }
  permissions {
    delete
  }
}
    `;