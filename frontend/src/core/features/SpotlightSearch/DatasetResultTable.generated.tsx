import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { WorkspaceDisplayFragmentFragmentDoc } from './WorkspaceDisplay.generated';
import { UserAvatar_UserFragmentDoc } from '../../../identity/features/UserAvatar.generated';
export type DatasetsPageFragment = { __typename?: 'DatasetResultPage', totalItems: number, pageNumber: number, totalPages: number, items: Array<{ __typename?: 'DatasetResult', score: number, dataset: { __typename?: 'Dataset', id: string, slug: string, name: string, description?: string | null, updatedAt: any, workspace?: { __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', code: string }> } | null, createdBy?: { __typename?: 'User', id: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null } }> };

export const DatasetsPageFragmentDoc = gql`
    fragment DatasetsPage on DatasetResultPage {
  items {
    dataset {
      id
      slug
      name
      description
      workspace {
        slug
        ...WorkspaceDisplayFragment
      }
      createdBy {
        id
        displayName
        ...UserAvatar_user
      }
      updatedAt
    }
    score
  }
  totalItems
  pageNumber
  totalPages
}
    ${WorkspaceDisplayFragmentFragmentDoc}
${UserAvatar_UserFragmentDoc}`;