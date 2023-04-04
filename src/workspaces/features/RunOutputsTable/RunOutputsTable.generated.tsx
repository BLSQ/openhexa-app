import * as Types from '../../../graphql-types';

import { gql } from '@apollo/client';
import { DownloadBucketObject_WorkspaceFragmentDoc } from '../DownloadBucketObject/DownloadBucketObject.generated';
export type RunOutputsTable_WorkspaceFragment = { __typename?: 'Workspace', slug: string, bucket: { __typename?: 'Bucket', name: string } };

export type RunOutputsTable_RunFragment = { __typename?: 'PipelineRun', id: string, outputs: Array<{ __typename?: 'PipelineRunOutput', name?: string | null, type: string, uri: string }> };

export const RunOutputsTable_WorkspaceFragmentDoc = gql`
    fragment RunOutputsTable_workspace on Workspace {
  ...DownloadBucketObject_workspace
  slug
  bucket {
    name
  }
}
    ${DownloadBucketObject_WorkspaceFragmentDoc}`;
export const RunOutputsTable_RunFragmentDoc = gql`
    fragment RunOutputsTable_run on PipelineRun {
  id
  outputs {
    name
    type
    uri
  }
}
    `;