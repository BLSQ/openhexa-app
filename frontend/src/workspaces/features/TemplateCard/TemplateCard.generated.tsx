import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { PipelineMetadataDisplay_TemplateFragmentDoc } from '../../../pipelines/features/PipelineMetadataDisplay/PipelineMetadataDisplay.generated';
import { User_UserFragmentDoc } from '../../../core/features/User/User.generated';
export type TemplateCard_TemplateFragment = { __typename?: 'PipelineTemplate', id: string, code: string, name: string, description?: string | null, publisher?: string | null, pipelinesCount: number, functionalType?: Types.PipelineFunctionalType | null, organization?: { __typename?: 'Organization', name: string, logo?: string | null } | null, currentVersion?: { __typename?: 'PipelineTemplateVersion', id: string, createdAt: any, user?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null } | null, tags: Array<{ __typename?: 'Tag', id: string, name: string }> };

export type TemplateCard_WorkspaceFragment = { __typename?: 'Workspace', slug: string };

export const TemplateCard_TemplateFragmentDoc = gql`
    fragment TemplateCard_template on PipelineTemplate {
  id
  code
  name
  description
  publisher
  pipelinesCount
  organization {
    name
    logo
  }
  ...PipelineMetadataDisplay_template
  currentVersion {
    id
    createdAt
    user {
      ...User_user
    }
  }
}
    ${PipelineMetadataDisplay_TemplateFragmentDoc}
${User_UserFragmentDoc}`;
export const TemplateCard_WorkspaceFragmentDoc = gql`
    fragment TemplateCard_workspace on Workspace {
  slug
}
    `;