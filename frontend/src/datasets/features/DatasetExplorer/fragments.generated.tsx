import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { DownloadVersionFile_FileFragmentDoc } from '../DownloadVersionFile/DownloadVersionFile.generated';
import { DatasetVersionFileSample_FileFragmentDoc } from '../DatasetVersionFileSample/DatasetVersionFileSample.generated';
import { DatasetVersionFileColumns_FileFragmentDoc } from '../DatasetVersionFileColumns/DatasetVersionFileColumns.generated';
export type DatasetExplorer_FileFragment = { __typename?: 'DatasetVersionFile', id: string, filename: string, createdAt: any, contentType: string, size: any, uri: string, downloadUrl?: string | null, targetId: any, properties?: any | null, createdBy?: { __typename?: 'User', displayName: string } | null, attributes: Array<{ __typename: 'MetadataAttribute', id: string, key: string, value?: any | null, label?: string | null, system: boolean }> };

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