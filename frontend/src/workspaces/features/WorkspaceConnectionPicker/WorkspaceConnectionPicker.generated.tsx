import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type WorkspaceConnectionPicker_WorkspaceFragment = { __typename?: 'Workspace', slug: string, connections: Array<{ __typename?: 'CustomConnection', id: string, name: string, slug: string, type: Types.ConnectionType } | { __typename?: 'DHIS2Connection', id: string, name: string, slug: string, type: Types.ConnectionType } | { __typename?: 'GCSConnection', id: string, name: string, slug: string, type: Types.ConnectionType } | { __typename?: 'IASOConnection', id: string, name: string, slug: string, type: Types.ConnectionType } | { __typename?: 'PostgreSQLConnection', id: string, name: string, slug: string, type: Types.ConnectionType } | { __typename?: 'S3Connection', id: string, name: string, slug: string, type: Types.ConnectionType }> };

export const WorkspaceConnectionPicker_WorkspaceFragmentDoc = gql`
    fragment WorkspaceConnectionPicker_workspace on Workspace {
  slug
  connections {
    id
    name
    slug
    type
  }
}
    `;