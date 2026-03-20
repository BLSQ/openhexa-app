import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { BucketObjectPicker_WorkspaceFragmentDoc } from '../BucketObjectPicker/BucketObjectPicker.generated';
export type CreatePipelineDialog_WorkspaceFragment = { __typename?: 'Workspace', slug: string };

export const CreatePipelineDialog_WorkspaceFragmentDoc = gql`
    fragment CreatePipelineDialog_workspace on Workspace {
  slug
  ...BucketObjectPicker_workspace
}
    ${BucketObjectPicker_WorkspaceFragmentDoc}`;