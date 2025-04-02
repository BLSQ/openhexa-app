import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type PipelinePublish_PipelineFragment = { __typename?: 'Pipeline', id: string, name?: string | null, description?: string | null, currentVersion?: { __typename?: 'PipelineVersion', id: string, versionName: string } | null, template?: { __typename?: 'PipelineTemplate', id: string, name: string } | null };

export type PipelinePublish_WorkspaceFragment = { __typename?: 'Workspace', slug: string };

export const PipelinePublish_PipelineFragmentDoc = gql`
    fragment PipelinePublish_pipeline on Pipeline {
  id
  name
  description
  currentVersion {
    id
    versionName
  }
  template {
    id
    name
  }
}
    `;
export const PipelinePublish_WorkspaceFragmentDoc = gql`
    fragment PipelinePublish_workspace on Workspace {
  slug
}
    `;