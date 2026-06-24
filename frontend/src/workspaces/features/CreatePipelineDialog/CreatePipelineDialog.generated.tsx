import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { BucketObjectPicker_WorkspaceFragmentDoc } from '../BucketObjectPicker/BucketObjectPicker.generated';
export type CreatePipelineDialog_WorkspaceFragment = { __typename?: 'Workspace', slug: string, organization?: { __typename?: 'Organization', id: string, aiSettings?: { __typename?: 'AiSettings', enabled?: boolean | null } | null } | null };

export const CreatePipelineDialog_WorkspaceFragmentDoc = gql`
    fragment CreatePipelineDialog_workspace on Workspace {
  slug
  organization {
    id
    aiSettings {
      enabled
    }
  }
  ...BucketObjectPicker_workspace
}
    ${BucketObjectPicker_WorkspaceFragmentDoc}`;