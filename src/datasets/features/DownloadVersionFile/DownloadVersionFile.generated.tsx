import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type DownloadVersionFile_FileFragment = { __typename?: 'DatasetVersionFile', id: string, filename: string };

export const DownloadVersionFile_FileFragmentDoc = gql`
    fragment DownloadVersionFile_file on DatasetVersionFile {
  id
  filename
}
    `;