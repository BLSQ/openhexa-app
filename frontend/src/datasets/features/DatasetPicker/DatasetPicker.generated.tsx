import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type DatasetPicker_WorkspaceFragment = { __typename?: 'Workspace', datasets: { __typename?: 'DatasetLinkPage', items: Array<{ __typename?: 'DatasetLink', id: string, dataset: { __typename?: 'Dataset', slug: string, name: string } }> } };

export const DatasetPicker_WorkspaceFragmentDoc = gql`
    fragment DatasetPicker_workspace on Workspace {
  datasets {
    items {
      id
      dataset {
        slug
        name
      }
    }
  }
}
    `;