import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type CreateWebappDialog_WorkspaceFragment = { __typename?: 'Workspace', slug: string, aiAvailable: boolean, organization: { __typename?: 'Organization', id: string, aiBudgetLimitReached: boolean } };

export const CreateWebappDialog_WorkspaceFragmentDoc = gql`
    fragment CreateWebappDialog_workspace on Workspace {
  slug
  aiAvailable
  organization {
    id
    aiBudgetLimitReached
  }
}
    `;