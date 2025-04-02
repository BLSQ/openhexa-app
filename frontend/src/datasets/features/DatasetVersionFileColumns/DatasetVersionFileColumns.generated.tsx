import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { ColumnMetadataDrawer_FileFragmentDoc } from '../ColumnMetadataDrawer/ColumnMetadataDrawer.generated';
export type DatasetVersionFileColumns_FileFragment = { __typename?: 'DatasetVersionFile', id: string, filename: string, targetId: any, properties?: any | null, attributes: Array<{ __typename: 'MetadataAttribute', id: string, key: string, value?: any | null, label?: string | null, system: boolean }> };

export type DatasetVersionFileColumns_VersionFragment = { __typename?: 'DatasetVersion', name: string, dataset: { __typename?: 'Dataset', slug: string, permissions: { __typename?: 'DatasetPermissions', update: boolean }, workspace?: { __typename?: 'Workspace', slug: string } | null } };

export const DatasetVersionFileColumns_FileFragmentDoc = gql`
    fragment DatasetVersionFileColumns_file on DatasetVersionFile {
  id
  filename
  ...ColumnMetadataDrawer_file
}
    ${ColumnMetadataDrawer_FileFragmentDoc}`;
export const DatasetVersionFileColumns_VersionFragmentDoc = gql`
    fragment DatasetVersionFileColumns_version on DatasetVersion {
  name
  dataset {
    slug
    permissions {
      update
    }
    workspace {
      slug
    }
  }
}
    `;