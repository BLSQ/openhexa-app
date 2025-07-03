import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type FilesEditor_FileFragment = { __typename?: 'FileNode', id: string, name: string, path: string, type: Types.FileType, content?: string | null, parentId?: string | null, autoSelect: boolean };

export const FilesEditor_FileFragmentDoc = gql`
    fragment FilesEditor_file on FileNode {
  id
  name
  path
  type
  content
  parentId
  autoSelect
}
    `;