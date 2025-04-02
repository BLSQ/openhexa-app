import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type DatabaseVariablesSection_WorkspaceFragment = { __typename?: 'Workspace', slug: string, database: { __typename?: 'Database', credentials?: { __typename?: 'DatabaseCredentials', dbName: string, username: string, password: string, host: string, port: number, url: string } | null } };

export const DatabaseVariablesSection_WorkspaceFragmentDoc = gql`
    fragment DatabaseVariablesSection_workspace on Workspace {
  slug
  database {
    credentials {
      dbName
      username
      password
      host
      port
      url
    }
  }
}
    `;