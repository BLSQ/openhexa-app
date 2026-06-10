import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { DatasetExplorer_FileFragmentDoc } from './fragments.generated';
import { DatasetVersionFileSample_VersionFragmentDoc } from '../DatasetVersionFileSample/DatasetVersionFileSample.generated';
import { DatasetVersionFileColumns_VersionFragmentDoc } from '../DatasetVersionFileColumns/DatasetVersionFileColumns.generated';
export type DatasetExplorer_VersionFragment = { __typename?: 'DatasetVersion', id: string, name: string, files: { __typename?: 'DatasetVersionFilePage', totalPages: number, pageNumber: number, totalItems: number, items: Array<{ __typename?: 'DatasetVersionFile', id: string, filename: string, createdAt: any, contentType: string, size: any, uri: string, downloadUrl?: string | null, targetId: any, properties?: any | null, createdBy?: { __typename?: 'User', displayName: string } | null, attributes: Array<{ __typename: 'MetadataAttribute', id: string, key: string, value?: any | null, label?: string | null, system: boolean }> }> }, dataset: { __typename?: 'Dataset', slug: string, workspace?: { __typename?: 'Workspace', slug: string } | null, permissions: { __typename?: 'DatasetPermissions', update: boolean } } };

export const DatasetExplorer_VersionFragmentDoc = gql`
    fragment DatasetExplorer_version on DatasetVersion {
  id
  files(page: $page, perPage: $perPage) {
    totalPages
    pageNumber
    totalItems
    items {
      ...DatasetExplorer_file
    }
  }
  ...DatasetVersionFileSample_version
  ...DatasetVersionFileColumns_version
}
    ${DatasetExplorer_FileFragmentDoc}
${DatasetVersionFileSample_VersionFragmentDoc}
${DatasetVersionFileColumns_VersionFragmentDoc}`;