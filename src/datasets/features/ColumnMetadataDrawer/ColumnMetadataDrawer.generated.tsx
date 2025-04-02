import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type ColumnMetadataDrawer_FileFragment = { __typename?: 'DatasetVersionFile', id: string, targetId: any, properties?: any | null, attributes: Array<{ __typename: 'MetadataAttribute', id: string, key: string, value?: any | null, label?: string | null, system: boolean }> };

export const ColumnMetadataDrawer_FileFragmentDoc = gql`
    fragment ColumnMetadataDrawer_file on DatasetVersionFile {
  id
  targetId
  attributes {
    id
    key
    value
    label
    system
    __typename
  }
  properties
}
    `;