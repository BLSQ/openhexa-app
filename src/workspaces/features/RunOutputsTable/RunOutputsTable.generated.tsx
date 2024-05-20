import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { DownloadBucketObject_WorkspaceFragmentDoc } from '../DownloadBucketObject/DownloadBucketObject.generated';
export type RunOutputsTable_WorkspaceFragment = { __typename?: 'Workspace', slug: string, bucket: { __typename?: 'Bucket', name: string } };

export type RunOutputsTable_RunFragment = { __typename?: 'PipelineRun', id: string, outputs: Array<{ __typename: 'BucketObject', name: string, key: string, path: string, type: Types.BucketObjectType } | { __typename: 'DatabaseTable', tableName: string } | { __typename: 'GenericOutput', genericName?: string | null, genericType: string, genericUri: string }>, datasetVersions: Array<{ __typename?: 'DatasetVersion', name: string, dataset: { __typename?: 'Dataset', slug: string, name: string } }> };

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
    __typename
    ... on GenericOutput {
      genericName: name
      genericType: type
      genericUri: uri
    }
    ... on BucketObject {
      name
      key
      path
      type
    }
    ... on DatabaseTable {
      tableName: name
    }
  }
  datasetVersions {
    name
    dataset {
      slug
      name
    }
  }
}
    `;