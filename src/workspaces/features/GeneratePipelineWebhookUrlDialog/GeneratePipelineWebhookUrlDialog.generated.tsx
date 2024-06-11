import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type GeneratePipelineWebhookUrlDialog_PipelineFragment = { __typename?: 'Pipeline', id: string, code: string };

export const GeneratePipelineWebhookUrlDialog_PipelineFragmentDoc = gql`
    fragment GeneratePipelineWebhookUrlDialog_pipeline on Pipeline {
  id
  code
}
    `;