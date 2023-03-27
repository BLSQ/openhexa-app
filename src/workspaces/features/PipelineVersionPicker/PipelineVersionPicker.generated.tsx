import * as Types from '../../../graphql-types';

import { gql } from '@apollo/client';
export type PipelineVersionPicker_PipelineFragment = { __typename?: 'Pipeline', id: string, versions: { __typename?: 'PipelineVersionPage', items: Array<{ __typename?: 'PipelineVersion', id: string, number: number, createdAt: any, parameters: any, user?: { __typename?: 'User', displayName: string } | null }> } };

export const PipelineVersionPicker_PipelineFragmentDoc = gql`
    fragment PipelineVersionPicker_pipeline on Pipeline {
  id
  versions {
    items {
      id
      number
      createdAt
      parameters
      user {
        displayName
      }
    }
  }
}
    `;