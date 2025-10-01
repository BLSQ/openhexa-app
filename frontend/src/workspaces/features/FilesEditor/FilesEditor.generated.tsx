import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type FilesEditor_FileFragment = { __typename?: 'FileNode', id: string, name: string, path: string, type: Types.BucketObjectType, content?: string | null, parentId?: string | null, autoSelect: boolean, language?: string | null, lineCount?: number | null };

export const FilesEditor_FileFragmentDoc = gql`
    fragment FilesEditor_file on FileNode {
  id
  name
  path
  type
  content
  parentId
  autoSelect
  language
  lineCount
}
    `;