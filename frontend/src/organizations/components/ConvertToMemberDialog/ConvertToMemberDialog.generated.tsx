import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type ConvertToMemberDialog_CollaboratorFragment = { __typename?: 'ExternalCollaborator', id: string, user: { __typename?: 'User', id: string, displayName: string, email: string } };

export const ConvertToMemberDialog_CollaboratorFragmentDoc = gql`
    fragment ConvertToMemberDialog_collaborator on ExternalCollaborator {
  id
  user {
    id
    displayName
    email
  }
}
    `;