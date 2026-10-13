import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type PublicFilesSettings_WorkspaceFragment = { __typename?: 'Workspace', slug: string, publicFilesEnabled: boolean, publicFilesUrl: any, permissions: { __typename?: 'WorkspacePermissions', managePublicFiles: boolean } };

export const PublicFilesSettings_WorkspaceFragmentDoc = gql`
    fragment PublicFilesSettings_workspace on Workspace {
  slug
  publicFilesEnabled
  publicFilesUrl
  permissions {
    managePublicFiles
  }
}
    `;