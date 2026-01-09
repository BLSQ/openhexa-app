import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type DatabaseVariablesSection_CredentialsFragment = { __typename?: 'DatabaseCredentials', dbName: string, username: string, password: string, host: string, port: number, url: string };

export const DatabaseVariablesSection_CredentialsFragmentDoc = gql`
    fragment DatabaseVariablesSection_credentials on DatabaseCredentials {
  dbName
  username
  password
  host
  port
  url
}
    `;