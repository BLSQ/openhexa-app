import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { BucketObjectPicker_WorkspaceFragmentDoc } from '../BucketObjectPicker/BucketObjectPicker.generated';
export type CreatePipelineDialog_WorkspaceFragment = { __typename?: 'Workspace', slug: string, permissions: { __typename?: 'WorkspacePermissions', generateToken: boolean }, organization: { __typename?: 'Organization', id: string, aiBudgetLimitReached: boolean, aiSettings?: { __typename?: 'AiSettings', enabled?: boolean | null } | null } };

export const CreatePipelineDialog_WorkspaceFragmentDoc = gql`
    fragment CreatePipelineDialog_workspace on Workspace {
  slug
  permissions {
    generateToken
  }
  organization {
    id
    aiSettings {
      enabled
    }
    aiBudgetLimitReached
  }
  ...BucketObjectPicker_workspace
}
    ${BucketObjectPicker_WorkspaceFragmentDoc}`;