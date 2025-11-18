import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { Tag_TagFragmentDoc } from '../../../core/features/Tag.generated';
export type PipelineMetadataDisplay_PipelineFragment = { __typename?: 'Pipeline', functionalType?: Types.PipelineFunctionalType | null, tags: Array<{ __typename?: 'Tag', id: string, name: string }> };

export type PipelineMetadataDisplay_TemplateFragment = { __typename?: 'PipelineTemplate', functionalType?: Types.PipelineFunctionalType | null, tags: Array<{ __typename?: 'Tag', id: string, name: string }> };

export const PipelineMetadataDisplay_PipelineFragmentDoc = gql`
    fragment PipelineMetadataDisplay_pipeline on Pipeline {
  functionalType
  tags {
    ...Tag_tag
  }
}
    ${Tag_TagFragmentDoc}`;
export const PipelineMetadataDisplay_TemplateFragmentDoc = gql`
    fragment PipelineMetadataDisplay_template on PipelineTemplate {
  functionalType
  tags {
    ...Tag_tag
  }
}
    ${Tag_TagFragmentDoc}`;