import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import { WorkspaceLayout_WorkspaceFragmentDoc } from '../../workspaces/layouts/WorkspaceLayout/WorkspaceLayout.generated';
import { UploadDatasetVersionDialog_DatasetLinkFragmentDoc } from '../features/UploadDatasetVersionDialog/UploadDatasetVersionDialog.generated';
import { PinDatasetButton_LinkFragmentDoc } from '../features/PinDatasetButton/PinDatasetButton.generated';
import { DatasetVersionPicker_VersionFragmentDoc } from '../features/DatasetVersionPicker/DatasetVersionPicker.generated';
export type DatasetLayout_WorkspaceFragment = { __typename?: 'Workspace', name: string, slug: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, countries: Array<{ __typename?: 'Country', flag: string, code: string }> };

export type DatasetLayout_DatasetLinkFragment = { __typename?: 'DatasetLink', id: string, isPinned: boolean, dataset: { __typename?: 'Dataset', slug: string, id: string, name: string, workspace?: { __typename?: 'Workspace', slug: string } | null, permissions: { __typename?: 'DatasetPermissions', delete: boolean, createVersion: boolean } }, workspace: { __typename?: 'Workspace', slug: string }, permissions: { __typename?: 'DatasetLinkPermissions', pin: boolean } };

export type DatasetLayout_VersionFragment = { __typename?: 'DatasetVersion', id: string, name: string, createdAt: any };

export const DatasetLayout_WorkspaceFragmentDoc = gql`
    fragment DatasetLayout_workspace on Workspace {
  ...WorkspaceLayout_workspace
  name
  slug
}
    ${WorkspaceLayout_WorkspaceFragmentDoc}`;
export const DatasetLayout_DatasetLinkFragmentDoc = gql`
    fragment DatasetLayout_datasetLink on DatasetLink {
  ...UploadDatasetVersionDialog_datasetLink
  ...PinDatasetButton_link
  dataset {
    workspace {
      slug
    }
    slug
    permissions {
      delete
      createVersion
    }
  }
}
    ${UploadDatasetVersionDialog_DatasetLinkFragmentDoc}
${PinDatasetButton_LinkFragmentDoc}`;
export const DatasetLayout_VersionFragmentDoc = gql`
    fragment DatasetLayout_version on DatasetVersion {
  id
  name
  ...DatasetVersionPicker_version
}
    ${DatasetVersionPicker_VersionFragmentDoc}`;