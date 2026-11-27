import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { BucketObjectPicker_WorkspaceFragmentDoc } from '../BucketObjectPicker/BucketObjectPicker.generated';
export type CreatePipelineDialog_WorkspaceFragment = { __typename?: 'Workspace', slug: string, aiAvailable: boolean, permissions: { __typename?: 'WorkspacePermissions', generateToken: boolean }, organization: { __typename?: 'Organization', id: string, aiBudgetLimitReached: boolean } };

export const CreatePipelineDialog_WorkspaceFragmentDoc = gql`
    fragment CreatePipelineDialog_workspace on Workspace {
  slug
  permissions {
    generateToken
  }
  aiAvailable
  organization {
    id
    aiBudgetLimitReached
  }
  ...BucketObjectPicker_workspace
}
    ${BucketObjectPicker_WorkspaceFragmentDoc}`;