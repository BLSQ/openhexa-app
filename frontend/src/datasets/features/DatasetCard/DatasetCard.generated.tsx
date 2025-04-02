import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type DatasetCard_LinkFragment = { __typename?: 'DatasetLink', id: string, dataset: { __typename?: 'Dataset', name: string, slug: string, description?: string | null, updatedAt: any, workspace?: { __typename?: 'Workspace', slug: string, name: string } | null }, workspace: { __typename?: 'Workspace', slug: string, name: string } };

export const DatasetCard_LinkFragmentDoc = gql`
    fragment DatasetCard_link on DatasetLink {
  dataset {
    name
    slug
    description
    updatedAt
    workspace {
      slug
      name
    }
  }
  id
  workspace {
    slug
    name
  }
}
    `;