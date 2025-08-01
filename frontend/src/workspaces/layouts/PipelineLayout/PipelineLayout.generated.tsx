import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { TabLayout_WorkspaceFragmentDoc } from '../TabLayout/TabLayout.generated';
import { PipelineVersionPicker_VersionFragmentDoc } from '../../features/PipelineVersionPicker/PipelineVersionPicker.generated';
import { DownloadPipelineVersion_VersionFragmentDoc } from '../../../pipelines/features/DownloadPipelineVersion/DownloadPipelineVersion.generated';
import { RunPipelineDialog_PipelineFragmentDoc, RunPipelineDialog_RunFragmentDoc } from '../../features/RunPipelineDialog/RunPipelineDialog.generated';
export type PipelineLayout_WorkspaceFragment = { __typename?: 'Workspace', name: string, slug: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, countries: Array<{ __typename?: 'Country', flag: string, code: string }>, organization?: { __typename?: 'Organization', id: string, name: string, shortName?: string | null } | null };

export type PipelineLayout_PipelineFragment = { __typename?: 'Pipeline', id: string, code: string, name?: string | null, type: Types.PipelineType, permissions: { __typename?: 'PipelinePermissions', run: boolean, delete: boolean, update: boolean, createTemplateVersion: { __typename?: 'CreateTemplateVersionPermission', isAllowed: boolean, reasons: Array<Types.CreateTemplateVersionPermissionReason> } }, template?: { __typename?: 'PipelineTemplate', id: string, name: string, code: string } | null, currentVersion?: { __typename?: 'PipelineVersion', id: string, name?: string | null, description?: string | null, config?: any | null, externalLink?: any | null, versionName: string, createdAt: any, templateVersion?: { __typename?: 'PipelineTemplateVersion', id: string } | null, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, help?: string | null, type: Types.ParameterType, widget?: Types.ParameterWidget | null, connection?: string | null, default?: any | null, required: boolean, choices?: Array<any> | null, multiple: boolean }>, user?: { __typename?: 'User', displayName: string } | null, pipeline: { __typename?: 'Pipeline', id: string, code: string } } | null, workspace: { __typename?: 'Workspace', slug: string } };

export const PipelineLayout_WorkspaceFragmentDoc = gql`
    fragment PipelineLayout_workspace on Workspace {
  ...TabLayout_workspace
}
    ${TabLayout_WorkspaceFragmentDoc}`;
export const PipelineLayout_PipelineFragmentDoc = gql`
    fragment PipelineLayout_pipeline on Pipeline {
  id
  code
  name
  permissions {
    run
    delete
    update
    createTemplateVersion {
      isAllowed
      reasons
    }
  }
  template {
    id
    name
    code
  }
  currentVersion {
    id
    name
    description
    config
    externalLink
    templateVersion {
      id
    }
    ...PipelineVersionPicker_version
    ...DownloadPipelineVersion_version
  }
  ...RunPipelineDialog_pipeline
}
    ${PipelineVersionPicker_VersionFragmentDoc}
${DownloadPipelineVersion_VersionFragmentDoc}
${RunPipelineDialog_PipelineFragmentDoc}`;