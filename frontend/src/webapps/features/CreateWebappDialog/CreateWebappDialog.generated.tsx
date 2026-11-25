import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type CreateWebappDialog_WorkspaceFragment = { __typename?: 'Workspace', slug: string, aiEnabled: boolean, organization: { __typename?: 'Organization', id: string, aiBudgetLimitReached: boolean, aiSettings?: { __typename?: 'AiSettings', enabled?: boolean | null } | null } };

export const CreateWebappDialog_WorkspaceFragmentDoc = gql`
    fragment CreateWebappDialog_workspace on Workspace {
  slug
  aiEnabled
  organization {
    id
    aiSettings {
      enabled
    }
    aiBudgetLimitReached
  }
}
    `;