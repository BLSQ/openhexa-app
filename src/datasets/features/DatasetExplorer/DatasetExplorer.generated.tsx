import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { DownloadVersionFile_FileFragmentDoc } from '../DownloadVersionFile/DownloadVersionFile.generated';
import { DatasetVersionFileSample_FileFragmentDoc } from '../DatasetVersionFileSample/DatasetVersionFileSample.generated';
import { DatasetVersionFileColumns_FileFragmentDoc } from '../DatasetVersionFileColumns/DatasetVersionFileColumns.generated';
export type DatasetExplorer_FileFragment = { __typename?: 'DatasetVersionFile', id: string, filename: string, createdAt: any, contentType: string, size: any, uri: string, downloadUrl?: string | null, createdBy?: { __typename?: 'User', displayName: string } | null };

export type DatasetExplorer_VersionFragment = { __typename?: 'DatasetVersion', id: string, files: { __typename?: 'DatasetVersionFilePage', items: Array<{ __typename?: 'DatasetVersionFile', id: string, filename: string, createdAt: any, contentType: string, size: any, uri: string, downloadUrl?: string | null, createdBy?: { __typename?: 'User', displayName: string } | null }> } };

export const DatasetExplorer_FileFragmentDoc = gql`
    fragment DatasetExplorer_file on DatasetVersionFile {
  id
  filename
  createdAt
  createdBy {
    displayName
  }
  ...DownloadVersionFile_file
  ...DatasetVersionFileSample_file
  ...DatasetVersionFileColumns_file
  contentType
  size
  uri
}
    ${DownloadVersionFile_FileFragmentDoc}
${DatasetVersionFileSample_FileFragmentDoc}
${DatasetVersionFileColumns_FileFragmentDoc}`;
export const DatasetExplorer_VersionFragmentDoc = gql`
    fragment DatasetExplorer_version on DatasetVersion {
  id
  files {
    items {
      ...DatasetExplorer_file
    }
  }
}
    ${DatasetExplorer_FileFragmentDoc}`;