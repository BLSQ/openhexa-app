import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type PipelineDelete_PipelineFragment = { __typename?: 'Pipeline', id: string, name?: string | null, code: string };

export type PipelineDelete_WorkspaceFragment = { __typename?: 'Workspace', slug: string };

export const PipelineDelete_PipelineFragmentDoc = gql`
    fragment PipelineDelete_pipeline on Pipeline {
  id
  name
  code
}
    `;
export const PipelineDelete_WorkspaceFragmentDoc = gql`
    fragment PipelineDelete_workspace on Workspace {
  slug
}
    `;