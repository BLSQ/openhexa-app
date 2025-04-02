import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type PipelineTemplateDialog_PipelineTemplateFragment = { __typename?: 'PipelineTemplate', id: string, name: string };

export const PipelineTemplateDialog_PipelineTemplateFragmentDoc = gql`
    fragment PipelineTemplateDialog_pipelineTemplate on PipelineTemplate {
  id
  name
}
    `;