import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import { ArchiveWorkspace_WorkspaceFragmentDoc } from '../features/ArchiveWorkspaceDialog/ArchiveWorkspaceDialog.generated';
import { InviteMemberWorkspace_WorkspaceFragmentDoc } from '../features/InviteMemberDialog/InviteMemberDialog.generated';
import { WorkspaceLayout_WorkspaceFragmentDoc } from '../layouts/WorkspaceLayout/WorkspaceLayout.generated';
import { CreatePipelineDialog_WorkspaceFragmentDoc } from '../features/CreatePipelineDialog/CreatePipelineDialog.generated';
import { PipelineCard_PipelineFragmentDoc } from '../features/PipelineCard/PipelineCard.generated';
import { User_UserFragmentDoc } from '../../core/features/User/User.generated';
import { PipelineRunStatusBadge_RunFragmentDoc } from '../../pipelines/features/PipelineRunStatusBadge.generated';
import { PipelineLayout_WorkspaceFragmentDoc, PipelineLayout_PipelineFragmentDoc } from '../layouts/PipelineLayout/PipelineLayout.generated';
import { RunPipelineDialog_PipelineFragmentDoc, RunPipelineDialog_RunFragmentDoc } from '../features/RunPipelineDialog/RunPipelineDialog.generated';
import { PipelineVersionParametersTable_VersionFragmentDoc } from '../../pipelines/features/PipelineVersionParametersTable/PipelineVersionParametersTable.generated';
import { PipelineVersionConfigDialog_VersionFragmentDoc } from '../features/PipelineVersionConfigDialog/PipelineVersionConfigDialog.generated';
import { UserColumn_UserFragmentDoc } from '../../core/components/DataGrid/UserColumn.generated';
import { PipelineRecipients_PipelineFragmentDoc } from '../features/PipelineRecipients/PipelineRecipients.generated';
import { PipelineVersionCard_VersionFragmentDoc } from '../../pipelines/features/PipelineVersionCard/PipelineVersionCard.generated';
import { RunOutputsTable_WorkspaceFragmentDoc, RunOutputsTable_RunFragmentDoc } from '../features/RunOutputsTable/RunOutputsTable.generated';
import { RunMessages_RunFragmentDoc } from '../../pipelines/features/RunMessages/RunMessages.generated';
import { RunLogs_RunFragmentDoc } from '../../pipelines/features/RunLogs/RunLogs.generated';
import { CreateDatasetDialog_WorkspaceFragmentDoc } from '../../datasets/features/CreateDatasetDialog/CreateDatasetDialog.generated';
import { DatasetCard_LinkFragmentDoc } from '../../datasets/features/DatasetCard/DatasetCard.generated';
import { PinDatasetButton_LinkFragmentDoc } from '../../datasets/features/PinDatasetButton/PinDatasetButton.generated';
import { DatasetLayout_WorkspaceFragmentDoc, DatasetLayout_DatasetLinkFragmentDoc, DatasetLayout_VersionFragmentDoc } from '../../datasets/layouts/DatasetLayout.generated';
import { DatasetLinksDataGrid_DatasetFragmentDoc } from '../../datasets/features/DatasetLinksDataGrid/DatasetLinksDataGrid.generated';
import { DatasetExplorer_VersionFragmentDoc } from '../../datasets/features/DatasetExplorer/DatasetExplorer.generated';
import { BucketExplorer_WorkspaceFragmentDoc, BucketExplorer_ObjectsFragmentDoc } from '../features/BucketExplorer/BucketExplorer.generated';
import { UploadObjectDialog_WorkspaceFragmentDoc } from '../features/UploadObjectDialog/UploadObjectDialog.generated';
import { CreateBucketFolderDialog_WorkspaceFragmentDoc } from '../features/CreateBucketFolderDialog/CreateBucketFolderDialog.generated';
import { DatabaseVariablesSection_WorkspaceFragmentDoc } from '../features/DatabaseVariablesSection/DatabaseVariablesSection.generated';
import { DatabaseTableDataGrid_TableFragmentDoc, DatabaseTableDataGrid_WorkspaceFragmentDoc } from '../features/DatabaseTableDataGrid/DatabaseTableDataGrid.generated';
import { CreateConnectionDialog_WorkspaceFragmentDoc } from '../features/CreateConnectionDialog/CreateConnectionDialog.generated';
import { ConnectionUsageSnippets_ConnectionFragmentDoc } from '../features/ConnectionUsageSnippets/ConnectionUsageSnippets.generated';
import { ConnectionFieldsSection_ConnectionFragmentDoc } from '../features/ConnectionFieldsSection/ConnectionFieldsSection.generated';
import { TemplateCard_TemplateFragmentDoc } from '../features/TemplateCard/TemplateCard.generated';
import { TemplateLayout_TemplateFragmentDoc } from '../layouts/TemplateLayout/TemplateLayout.generated';
import { TemplateVersionCard_VersionFragmentDoc } from '../../pipelines/features/TemplateVersionCard/TemplateVersionCard.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type WorkspacesPageQueryVariables = Types.Exact<{ [key: string]: never; }>;


export type WorkspacesPageQuery = { __typename?: 'Query', workspaces: { __typename?: 'WorkspacePage', items: Array<{ __typename?: 'Workspace', slug: string }> } };

export type WorkspacePageQueryVariables = Types.Exact<{
  slug: Types.Scalars['String']['input'];
}>;


export type WorkspacePageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string, description?: string | null, dockerImage?: string | null, countries: Array<{ __typename?: 'Country', code: string, flag: string, name: string }>, permissions: { __typename?: 'WorkspacePermissions', delete: boolean, update: boolean, manageMembers: boolean, launchNotebookServer: boolean } } | null };

export type WorkspacePipelinesPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type WorkspacePipelinesPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, countries: Array<{ __typename?: 'Country', flag: string, code: string }> } | null, pipelines: { __typename?: 'PipelinesPage', totalItems: number, totalPages: number, pageNumber: number, items: Array<{ __typename?: 'Pipeline', id: string, code: string, name?: string | null, schedule?: string | null, description?: string | null, type: Types.PipelineType, currentVersion?: { __typename?: 'PipelineVersion', createdAt: any, user?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null } | null, lastRuns: { __typename?: 'PipelineRunPage', items: Array<{ __typename?: 'PipelineRun', id: string, status: Types.PipelineRunStatus }> } }> } };

export type WorkspaceNotebooksPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
}>;


export type WorkspaceNotebooksPageQuery = { __typename?: 'Query', notebooksUrl: any, workspace?: { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', launchNotebookServer: boolean, manageMembers: boolean, update: boolean }, countries: Array<{ __typename?: 'Country', flag: string, code: string }> } | null };

export type WorkspacePipelinePageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  pipelineCode: Types.Scalars['String']['input'];
}>;


export type WorkspacePipelinePageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, countries: Array<{ __typename?: 'Country', flag: string, code: string }> } | null, pipeline?: { __typename?: 'Pipeline', webhookUrl?: string | null, webhookEnabled: boolean, id: string, createdAt: any, code: string, name?: string | null, description?: string | null, schedule?: string | null, type: Types.PipelineType, notebookPath?: string | null, hasNewTemplateVersions: boolean, permissions: { __typename?: 'PipelinePermissions', run: boolean, update: boolean, schedule: boolean, delete: boolean, createVersion: boolean, createTemplateVersion: boolean }, sourceTemplate?: { __typename?: 'PipelineTemplate', id: string, code: string, name: string } | null, newTemplateVersions?: Array<{ __typename?: 'PipelineTemplateVersion', id: string, changelog?: string | null, versionNumber: number, createdAt: any }> | null, currentVersion?: { __typename?: 'PipelineVersion', id: string, versionName: string, description?: string | null, config?: any | null, externalLink?: any | null, name?: string | null, isLatestVersion: boolean, createdAt: any, templateVersion?: { __typename?: 'PipelineTemplateVersion', id: string } | null, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, multiple: boolean, type: Types.ParameterType, help?: string | null, required: boolean, choices?: Array<any> | null, default?: any | null }>, pipeline: { __typename?: 'Pipeline', id: string, schedule?: string | null, code: string, workspace: { __typename?: 'Workspace', slug: string } }, user?: { __typename?: 'User', displayName: string } | null } | null, recipients: Array<{ __typename?: 'PipelineRecipient', user: { __typename?: 'User', id: string, displayName: string } }>, workspace: { __typename?: 'Workspace', slug: string }, template?: { __typename?: 'PipelineTemplate', id: string, name: string, code: string } | null } | null };

export type WorkspacePipelineRunsPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  pipelineCode: Types.Scalars['String']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type WorkspacePipelineRunsPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, countries: Array<{ __typename?: 'Country', flag: string, code: string }> } | null, pipeline?: { __typename?: 'Pipeline', id: string, type: Types.PipelineType, code: string, name?: string | null, runs: { __typename?: 'PipelineRunPage', totalItems: number, totalPages: number, pageNumber: number, items: Array<{ __typename?: 'PipelineRun', id: string, executionDate?: any | null, duration?: number | null, triggerMode?: Types.PipelineRunTrigger | null, status: Types.PipelineRunStatus, version?: { __typename?: 'PipelineVersion', versionName: string, createdAt: any, user?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null } | null, user?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null }> }, permissions: { __typename?: 'PipelinePermissions', run: boolean, delete: boolean, update: boolean, createTemplateVersion: boolean }, template?: { __typename?: 'PipelineTemplate', id: string, name: string, code: string } | null, currentVersion?: { __typename?: 'PipelineVersion', id: string, name?: string | null, description?: string | null, config?: any | null, externalLink?: any | null, versionName: string, createdAt: any, templateVersion?: { __typename?: 'PipelineTemplateVersion', id: string } | null, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, help?: string | null, type: Types.ParameterType, default?: any | null, required: boolean, choices?: Array<any> | null, multiple: boolean }>, user?: { __typename?: 'User', displayName: string } | null, pipeline: { __typename?: 'Pipeline', id: string, code: string } } | null, workspace: { __typename?: 'Workspace', slug: string } } | null };

export type WorkspacePipelineNotificationsPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  pipelineCode: Types.Scalars['String']['input'];
}>;


export type WorkspacePipelineNotificationsPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', name: string, slug: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, countries: Array<{ __typename?: 'Country', flag: string, code: string }> } | null, pipeline?: { __typename?: 'Pipeline', id: string, code: string, type: Types.PipelineType, schedule?: string | null, name?: string | null, permissions: { __typename?: 'PipelinePermissions', schedule: boolean, update: boolean, run: boolean, delete: boolean, createTemplateVersion: boolean }, template?: { __typename?: 'PipelineTemplate', id: string, name: string, code: string } | null, currentVersion?: { __typename?: 'PipelineVersion', id: string, name?: string | null, description?: string | null, config?: any | null, externalLink?: any | null, versionName: string, createdAt: any, templateVersion?: { __typename?: 'PipelineTemplateVersion', id: string } | null, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, help?: string | null, type: Types.ParameterType, default?: any | null, required: boolean, choices?: Array<any> | null, multiple: boolean }>, user?: { __typename?: 'User', displayName: string } | null, pipeline: { __typename?: 'Pipeline', id: string, code: string } } | null, workspace: { __typename?: 'Workspace', slug: string } } | null };

export type WorkspacePipelineVersionsPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  pipelineCode: Types.Scalars['String']['input'];
  page: Types.Scalars['Int']['input'];
  perPage: Types.Scalars['Int']['input'];
}>;


export type WorkspacePipelineVersionsPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, countries: Array<{ __typename?: 'Country', flag: string, code: string }> } | null, pipeline?: { __typename?: 'Pipeline', id: string, code: string, name?: string | null, currentVersion?: { __typename?: 'PipelineVersion', id: string } | null, versions: { __typename?: 'PipelineVersionPage', totalItems: number, totalPages: number, items: Array<{ __typename?: 'PipelineVersion', id: string, versionName: string, name?: string | null, description?: string | null, externalLink?: any | null, isLatestVersion: boolean, createdAt: any, user?: { __typename?: 'User', displayName: string } | null, permissions: { __typename?: 'PipelineVersionPermissions', update: boolean, delete: boolean }, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, type: Types.ParameterType, multiple: boolean, required: boolean, help?: string | null }>, pipeline: { __typename?: 'Pipeline', id: string, code: string }, templateVersion?: { __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number, template: { __typename?: 'PipelineTemplate', id: string, name: string } } | null }> } } | null };

export type WorkspacePipelineStartPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
}>;


export type WorkspacePipelineStartPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, countries: Array<{ __typename?: 'Country', flag: string, code: string }> } | null };

export type WorkspacePipelineRunPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  runId: Types.Scalars['UUID']['input'];
}>;


export type WorkspacePipelineRunPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string, bucket: { __typename?: 'Bucket', name: string }, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, countries: Array<{ __typename?: 'Country', flag: string, code: string }> } | null, pipelineRun?: { __typename?: 'PipelineRun', id: string, timeout?: number | null, config: any, executionDate?: any | null, duration?: number | null, triggerMode?: Types.PipelineRunTrigger | null, status: Types.PipelineRunStatus, logs?: string | null, version?: { __typename?: 'PipelineVersion', versionName: string, id: string, createdAt: any, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, multiple: boolean, type: Types.ParameterType, help?: string | null, required: boolean, choices?: Array<any> | null, default?: any | null }>, user?: { __typename?: 'User', displayName: string } | null } | null, pipeline: { __typename?: 'Pipeline', id: string, code: string, name?: string | null, type: Types.PipelineType, notebookPath?: string | null, permissions: { __typename?: 'PipelinePermissions', stopPipeline: boolean, run: boolean }, workspace: { __typename?: 'Workspace', slug: string }, currentVersion?: { __typename?: 'PipelineVersion', id: string } | null }, user?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null, stoppedBy?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null, outputs: Array<{ __typename: 'BucketObject', name: string, key: string, path: string, type: Types.BucketObjectType } | { __typename: 'DatabaseTable', tableName: string } | { __typename: 'GenericOutput', genericName?: string | null, genericType: string, genericUri: string }>, datasetVersions: Array<{ __typename?: 'DatasetVersion', name: string, dataset: { __typename?: 'Dataset', slug: string, name: string } }>, messages: Array<{ __typename?: 'PipelineRunMessage', message: string, timestamp?: any | null, priority: Types.MessagePriority }> } | null };

export type WorkspaceDatasetsPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  query?: Types.InputMaybe<Types.Scalars['String']['input']>;
}>;


export type WorkspaceDatasetsPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', createDataset: boolean, manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, pinnedDatasets: { __typename?: 'DatasetLinkPage', items: Array<{ __typename?: 'DatasetLink', id: string, dataset: { __typename?: 'Dataset', name: string, slug: string, description?: string | null, updatedAt: any, workspace?: { __typename?: 'Workspace', slug: string, name: string } | null }, workspace: { __typename?: 'Workspace', slug: string, name: string } }> }, datasets: { __typename?: 'DatasetLinkPage', totalItems: number, totalPages: number, pageNumber: number, items: Array<{ __typename?: 'DatasetLink', id: string, isPinned: boolean, dataset: { __typename?: 'Dataset', id: string, name: string, slug: string, description?: string | null, updatedAt: any, workspace?: { __typename?: 'Workspace', slug: string, name: string } | null, permissions: { __typename?: 'DatasetPermissions', update: boolean, delete: boolean }, createdBy?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null }, permissions: { __typename?: 'DatasetLinkPermissions', pin: boolean } }> }, countries: Array<{ __typename?: 'Country', flag: string, code: string }> } | null };

export type WorkspaceDatasetIndexPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  datasetSlug: Types.Scalars['String']['input'];
  versionId: Types.Scalars['ID']['input'];
  isSpecificVersion: Types.Scalars['Boolean']['input'];
}>;


export type WorkspaceDatasetIndexPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, countries: Array<{ __typename?: 'Country', flag: string, code: string }> } | null, datasetLink?: { __typename?: 'DatasetLink', id: string, isPinned: boolean, dataset: { __typename?: 'Dataset', description?: string | null, updatedAt: any, createdAt: any, slug: string, id: string, name: string, permissions: { __typename?: 'DatasetPermissions', update: boolean, delete: boolean, createVersion: boolean }, workspace?: { __typename?: 'Workspace', name: string, slug: string } | null, createdBy?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null, version?: { __typename?: 'DatasetVersion', id: string, createdAt: any, changelog?: string | null, name: string, createdBy?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null, permissions: { __typename?: 'DatasetVersionPermissions', update: boolean } } | null, latestVersion?: { __typename?: 'DatasetVersion', id: string, changelog?: string | null, createdAt: any, name: string, createdBy?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null, permissions: { __typename?: 'DatasetVersionPermissions', update: boolean } } | null }, workspace: { __typename?: 'Workspace', slug: string }, permissions: { __typename?: 'DatasetLinkPermissions', pin: boolean } } | null };

export type WorkspaceDatasetAccessPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  datasetSlug: Types.Scalars['String']['input'];
  versionId: Types.Scalars['ID']['input'];
  isSpecificVersion: Types.Scalars['Boolean']['input'];
}>;


export type WorkspaceDatasetAccessPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, countries: Array<{ __typename?: 'Country', flag: string, code: string }> } | null, datasetLink?: { __typename?: 'DatasetLink', id: string, isPinned: boolean, dataset: { __typename?: 'Dataset', name: string, slug: string, id: string, permissions: { __typename?: 'DatasetPermissions', update: boolean, delete: boolean, createVersion: boolean }, version?: { __typename?: 'DatasetVersion', id: string, name: string, createdAt: any } | null, latestVersion?: { __typename?: 'DatasetVersion', id: string, name: string, createdAt: any } | null, workspace?: { __typename?: 'Workspace', slug: string } | null }, workspace: { __typename?: 'Workspace', slug: string }, permissions: { __typename?: 'DatasetLinkPermissions', pin: boolean } } | null };

export type WorkspaceDatasetFilesPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  datasetSlug: Types.Scalars['String']['input'];
  versionId: Types.Scalars['ID']['input'];
  isSpecificVersion: Types.Scalars['Boolean']['input'];
}>;


export type WorkspaceDatasetFilesPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, countries: Array<{ __typename?: 'Country', flag: string, code: string }> } | null, datasetLink?: { __typename?: 'DatasetLink', id: string, isPinned: boolean, dataset: { __typename?: 'Dataset', name: string, slug: string, id: string, version?: { __typename?: 'DatasetVersion', id: string, name: string, createdAt: any, files: { __typename?: 'DatasetVersionFilePage', items: Array<{ __typename?: 'DatasetVersionFile', id: string, filename: string, createdAt: any, contentType: string, size: any, uri: string, downloadUrl?: string | null, targetId: any, properties?: any | null, createdBy?: { __typename?: 'User', displayName: string } | null, attributes: Array<{ __typename: 'MetadataAttribute', id: string, key: string, value?: any | null, label?: string | null, system: boolean }> }> }, dataset: { __typename?: 'Dataset', slug: string, workspace?: { __typename?: 'Workspace', slug: string } | null, permissions: { __typename?: 'DatasetPermissions', update: boolean } } } | null, latestVersion?: { __typename?: 'DatasetVersion', id: string, name: string, createdAt: any, files: { __typename?: 'DatasetVersionFilePage', items: Array<{ __typename?: 'DatasetVersionFile', id: string, filename: string, createdAt: any, contentType: string, size: any, uri: string, downloadUrl?: string | null, targetId: any, properties?: any | null, createdBy?: { __typename?: 'User', displayName: string } | null, attributes: Array<{ __typename: 'MetadataAttribute', id: string, key: string, value?: any | null, label?: string | null, system: boolean }> }> }, dataset: { __typename?: 'Dataset', slug: string, workspace?: { __typename?: 'Workspace', slug: string } | null, permissions: { __typename?: 'DatasetPermissions', update: boolean } } } | null, workspace?: { __typename?: 'Workspace', slug: string } | null, permissions: { __typename?: 'DatasetPermissions', delete: boolean, createVersion: boolean } }, workspace: { __typename?: 'Workspace', slug: string }, permissions: { __typename?: 'DatasetLinkPermissions', pin: boolean } } | null };

export type WorkspaceFilesPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  page: Types.Scalars['Int']['input'];
  perPage: Types.Scalars['Int']['input'];
  prefix: Types.Scalars['String']['input'];
  query?: Types.InputMaybe<Types.Scalars['String']['input']>;
  ignoreHiddenFiles?: Types.InputMaybe<Types.Scalars['Boolean']['input']>;
}>;


export type WorkspaceFilesPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string, bucket: { __typename?: 'Bucket', name: string, objects: { __typename?: 'BucketObjectPage', hasNextPage: boolean, hasPreviousPage: boolean, pageNumber: number, items: Array<{ __typename?: 'BucketObject', key: string, name: string, path: string, size?: any | null, updatedAt?: any | null, type: Types.BucketObjectType }> } }, permissions: { __typename?: 'WorkspacePermissions', createObject: boolean, deleteObject: boolean, manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, countries: Array<{ __typename?: 'Country', flag: string, code: string }> } | null };

export type WorkspaceDatabasesPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type WorkspaceDatabasesPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', launchNotebookServer: boolean, manageMembers: boolean, update: boolean }, database: { __typename?: 'Database', tables: { __typename?: 'DatabaseTablePage', totalPages: number, totalItems: number, items: Array<{ __typename?: 'DatabaseTable', name: string, count?: number | null }> }, credentials?: { __typename?: 'DatabaseCredentials', dbName: string, username: string, password: string, host: string, port: number, url: string } | null }, countries: Array<{ __typename?: 'Country', flag: string, code: string }> } | null };

export type WorkspaceDatabaseTablePageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  tableName: Types.Scalars['String']['input'];
}>;


export type WorkspaceDatabaseTablePageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', deleteDatabaseTable: boolean, manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, database: { __typename?: 'Database', table?: { __typename?: 'DatabaseTable', name: string, count?: number | null, columns: Array<{ __typename?: 'TableColumn', name: string, type: string }> } | null }, countries: Array<{ __typename?: 'Country', flag: string, code: string }> } | null };

export type ConnectionsPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
}>;


export type ConnectionsPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', update: boolean, createConnection: boolean, manageMembers: boolean, launchNotebookServer: boolean }, connections: Array<{ __typename?: 'CustomConnection', id: string, description?: string | null, name: string, type: Types.ConnectionType, slug: string, updatedAt?: any | null, permissions: { __typename?: 'ConnectionPermissions', update: boolean, delete: boolean } } | { __typename?: 'DHIS2Connection', id: string, description?: string | null, name: string, type: Types.ConnectionType, slug: string, updatedAt?: any | null, permissions: { __typename?: 'ConnectionPermissions', update: boolean, delete: boolean } } | { __typename?: 'GCSConnection', id: string, description?: string | null, name: string, type: Types.ConnectionType, slug: string, updatedAt?: any | null, permissions: { __typename?: 'ConnectionPermissions', update: boolean, delete: boolean } } | { __typename?: 'IASOConnection', id: string, description?: string | null, name: string, type: Types.ConnectionType, slug: string, updatedAt?: any | null, permissions: { __typename?: 'ConnectionPermissions', update: boolean, delete: boolean } } | { __typename?: 'PostgreSQLConnection', id: string, description?: string | null, name: string, type: Types.ConnectionType, slug: string, updatedAt?: any | null, permissions: { __typename?: 'ConnectionPermissions', update: boolean, delete: boolean } } | { __typename?: 'S3Connection', id: string, description?: string | null, name: string, type: Types.ConnectionType, slug: string, updatedAt?: any | null, permissions: { __typename?: 'ConnectionPermissions', update: boolean, delete: boolean } }>, countries: Array<{ __typename?: 'Country', flag: string, code: string }> } | null };

export type ConnectionPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  connectionId: Types.Scalars['UUID']['input'];
}>;


export type ConnectionPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', launchNotebookServer: boolean, manageMembers: boolean, update: boolean }, countries: Array<{ __typename?: 'Country', flag: string, code: string }> } | null, connection?: { __typename?: 'CustomConnection', id: string, name: string, slug: string, description?: string | null, type: Types.ConnectionType, createdAt: any, permissions: { __typename?: 'ConnectionPermissions', update: boolean, delete: boolean }, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> } | { __typename?: 'DHIS2Connection', id: string, name: string, slug: string, description?: string | null, type: Types.ConnectionType, createdAt: any, permissions: { __typename?: 'ConnectionPermissions', update: boolean, delete: boolean }, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> } | { __typename?: 'GCSConnection', id: string, name: string, slug: string, description?: string | null, type: Types.ConnectionType, createdAt: any, permissions: { __typename?: 'ConnectionPermissions', update: boolean, delete: boolean }, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> } | { __typename?: 'IASOConnection', id: string, name: string, slug: string, description?: string | null, type: Types.ConnectionType, createdAt: any, permissions: { __typename?: 'ConnectionPermissions', update: boolean, delete: boolean }, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> } | { __typename?: 'PostgreSQLConnection', id: string, name: string, slug: string, description?: string | null, type: Types.ConnectionType, createdAt: any, permissions: { __typename?: 'ConnectionPermissions', update: boolean, delete: boolean }, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> } | { __typename?: 'S3Connection', id: string, name: string, slug: string, description?: string | null, type: Types.ConnectionType, createdAt: any, permissions: { __typename?: 'ConnectionPermissions', update: boolean, delete: boolean }, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> } | null };

export type CheckWorkspaceAvailabilityQueryVariables = Types.Exact<{
  slug: Types.Scalars['String']['input'];
}>;


export type CheckWorkspaceAvailabilityQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string } | null };

export type WorkspaceTemplatesPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type WorkspaceTemplatesPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, countries: Array<{ __typename?: 'Country', flag: string, code: string }> } | null, pipelineTemplates: { __typename?: 'PipelineTemplatePage', totalItems: number, totalPages: number, pageNumber: number, items: Array<{ __typename?: 'PipelineTemplate', id: string, code: string, name: string, description?: string | null, currentVersion?: { __typename?: 'PipelineTemplateVersion', id: string, createdAt: any, user?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null } | null }> } };

export type WorkspaceTemplatePageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  templateCode: Types.Scalars['String']['input'];
}>;


export type WorkspaceTemplatePageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, countries: Array<{ __typename?: 'Country', flag: string, code: string }> } | null, template?: { __typename?: 'PipelineTemplate', id: string, code: string, name: string, description?: string | null, permissions: { __typename?: 'PipelineTemplatePermissions', update: boolean, delete: boolean }, currentVersion?: { __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number } | null } | null };

export type WorkspaceTemplateVersionsPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  templateCode: Types.Scalars['String']['input'];
  page: Types.Scalars['Int']['input'];
  perPage: Types.Scalars['Int']['input'];
}>;


export type WorkspaceTemplateVersionsPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, countries: Array<{ __typename?: 'Country', flag: string, code: string }> } | null, template?: { __typename?: 'PipelineTemplate', id: string, code: string, name: string, currentVersion?: { __typename?: 'PipelineTemplateVersion', id: string } | null, versions: { __typename?: 'TemplateVersionPage', totalItems: number, totalPages: number, items: Array<{ __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number, changelog?: string | null, createdAt: any, isLatestVersion: boolean, user?: { __typename?: 'User', displayName: string } | null, permissions: { __typename?: 'PipelineTemplateVersionPermissions', update: boolean, delete: boolean }, template: { __typename?: 'PipelineTemplate', id: string, code: string } }> } } | null };


export const WorkspacesPageDocument = gql`
    query WorkspacesPage {
  workspaces(page: 1, perPage: 1) {
    items {
      slug
    }
  }
}
    `;

/**
 * __useWorkspacesPageQuery__
 *
 * To run a query within a React component, call `useWorkspacesPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspacesPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspacesPageQuery({
 *   variables: {
 *   },
 * });
 */
export function useWorkspacesPageQuery(baseOptions?: Apollo.QueryHookOptions<WorkspacesPageQuery, WorkspacesPageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspacesPageQuery, WorkspacesPageQueryVariables>(WorkspacesPageDocument, options);
      }
export function useWorkspacesPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspacesPageQuery, WorkspacesPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspacesPageQuery, WorkspacesPageQueryVariables>(WorkspacesPageDocument, options);
        }
export function useWorkspacesPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspacesPageQuery, WorkspacesPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspacesPageQuery, WorkspacesPageQueryVariables>(WorkspacesPageDocument, options);
        }
export type WorkspacesPageQueryHookResult = ReturnType<typeof useWorkspacesPageQuery>;
export type WorkspacesPageLazyQueryHookResult = ReturnType<typeof useWorkspacesPageLazyQuery>;
export type WorkspacesPageSuspenseQueryHookResult = ReturnType<typeof useWorkspacesPageSuspenseQuery>;
export type WorkspacesPageQueryResult = Apollo.QueryResult<WorkspacesPageQuery, WorkspacesPageQueryVariables>;
export const WorkspacePageDocument = gql`
    query WorkspacePage($slug: String!) {
  workspace(slug: $slug) {
    slug
    name
    description
    dockerImage
    countries {
      code
      flag
      name
    }
    permissions {
      delete
      update
      manageMembers
    }
    ...ArchiveWorkspace_workspace
    ...InviteMemberWorkspace_workspace
    ...WorkspaceLayout_workspace
  }
}
    ${ArchiveWorkspace_WorkspaceFragmentDoc}
${InviteMemberWorkspace_WorkspaceFragmentDoc}
${WorkspaceLayout_WorkspaceFragmentDoc}`;

/**
 * __useWorkspacePageQuery__
 *
 * To run a query within a React component, call `useWorkspacePageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspacePageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspacePageQuery({
 *   variables: {
 *      slug: // value for 'slug'
 *   },
 * });
 */
export function useWorkspacePageQuery(baseOptions: Apollo.QueryHookOptions<WorkspacePageQuery, WorkspacePageQueryVariables> & ({ variables: WorkspacePageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspacePageQuery, WorkspacePageQueryVariables>(WorkspacePageDocument, options);
      }
export function useWorkspacePageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspacePageQuery, WorkspacePageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspacePageQuery, WorkspacePageQueryVariables>(WorkspacePageDocument, options);
        }
export function useWorkspacePageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspacePageQuery, WorkspacePageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspacePageQuery, WorkspacePageQueryVariables>(WorkspacePageDocument, options);
        }
export type WorkspacePageQueryHookResult = ReturnType<typeof useWorkspacePageQuery>;
export type WorkspacePageLazyQueryHookResult = ReturnType<typeof useWorkspacePageLazyQuery>;
export type WorkspacePageSuspenseQueryHookResult = ReturnType<typeof useWorkspacePageSuspenseQuery>;
export type WorkspacePageQueryResult = Apollo.QueryResult<WorkspacePageQuery, WorkspacePageQueryVariables>;
export const WorkspacePipelinesPageDocument = gql`
    query WorkspacePipelinesPage($workspaceSlug: String!, $page: Int, $perPage: Int) {
  workspace(slug: $workspaceSlug) {
    slug
    name
    ...WorkspaceLayout_workspace
    ...CreatePipelineDialog_workspace
  }
  pipelines(workspaceSlug: $workspaceSlug, page: $page, perPage: $perPage) {
    items {
      ...PipelineCard_pipeline
    }
    totalItems
    totalPages
    pageNumber
  }
}
    ${WorkspaceLayout_WorkspaceFragmentDoc}
${CreatePipelineDialog_WorkspaceFragmentDoc}
${PipelineCard_PipelineFragmentDoc}`;

/**
 * __useWorkspacePipelinesPageQuery__
 *
 * To run a query within a React component, call `useWorkspacePipelinesPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspacePipelinesPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspacePipelinesPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useWorkspacePipelinesPageQuery(baseOptions: Apollo.QueryHookOptions<WorkspacePipelinesPageQuery, WorkspacePipelinesPageQueryVariables> & ({ variables: WorkspacePipelinesPageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspacePipelinesPageQuery, WorkspacePipelinesPageQueryVariables>(WorkspacePipelinesPageDocument, options);
      }
export function useWorkspacePipelinesPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspacePipelinesPageQuery, WorkspacePipelinesPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspacePipelinesPageQuery, WorkspacePipelinesPageQueryVariables>(WorkspacePipelinesPageDocument, options);
        }
export function useWorkspacePipelinesPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspacePipelinesPageQuery, WorkspacePipelinesPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspacePipelinesPageQuery, WorkspacePipelinesPageQueryVariables>(WorkspacePipelinesPageDocument, options);
        }
export type WorkspacePipelinesPageQueryHookResult = ReturnType<typeof useWorkspacePipelinesPageQuery>;
export type WorkspacePipelinesPageLazyQueryHookResult = ReturnType<typeof useWorkspacePipelinesPageLazyQuery>;
export type WorkspacePipelinesPageSuspenseQueryHookResult = ReturnType<typeof useWorkspacePipelinesPageSuspenseQuery>;
export type WorkspacePipelinesPageQueryResult = Apollo.QueryResult<WorkspacePipelinesPageQuery, WorkspacePipelinesPageQueryVariables>;
export const WorkspaceNotebooksPageDocument = gql`
    query WorkspaceNotebooksPage($workspaceSlug: String!) {
  notebooksUrl
  workspace(slug: $workspaceSlug) {
    slug
    permissions {
      launchNotebookServer
    }
    ...WorkspaceLayout_workspace
  }
}
    ${WorkspaceLayout_WorkspaceFragmentDoc}`;

/**
 * __useWorkspaceNotebooksPageQuery__
 *
 * To run a query within a React component, call `useWorkspaceNotebooksPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspaceNotebooksPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspaceNotebooksPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *   },
 * });
 */
export function useWorkspaceNotebooksPageQuery(baseOptions: Apollo.QueryHookOptions<WorkspaceNotebooksPageQuery, WorkspaceNotebooksPageQueryVariables> & ({ variables: WorkspaceNotebooksPageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspaceNotebooksPageQuery, WorkspaceNotebooksPageQueryVariables>(WorkspaceNotebooksPageDocument, options);
      }
export function useWorkspaceNotebooksPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspaceNotebooksPageQuery, WorkspaceNotebooksPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspaceNotebooksPageQuery, WorkspaceNotebooksPageQueryVariables>(WorkspaceNotebooksPageDocument, options);
        }
export function useWorkspaceNotebooksPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspaceNotebooksPageQuery, WorkspaceNotebooksPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspaceNotebooksPageQuery, WorkspaceNotebooksPageQueryVariables>(WorkspaceNotebooksPageDocument, options);
        }
export type WorkspaceNotebooksPageQueryHookResult = ReturnType<typeof useWorkspaceNotebooksPageQuery>;
export type WorkspaceNotebooksPageLazyQueryHookResult = ReturnType<typeof useWorkspaceNotebooksPageLazyQuery>;
export type WorkspaceNotebooksPageSuspenseQueryHookResult = ReturnType<typeof useWorkspaceNotebooksPageSuspenseQuery>;
export type WorkspaceNotebooksPageQueryResult = Apollo.QueryResult<WorkspaceNotebooksPageQuery, WorkspaceNotebooksPageQueryVariables>;
export const WorkspacePipelinePageDocument = gql`
    query WorkspacePipelinePage($workspaceSlug: String!, $pipelineCode: String!) {
  workspace(slug: $workspaceSlug) {
    slug
    name
    ...PipelineLayout_workspace
  }
  pipeline: pipelineByCode(workspaceSlug: $workspaceSlug, code: $pipelineCode) {
    ...RunPipelineDialog_pipeline
    ...PipelineLayout_pipeline
    permissions {
      run
      update
      schedule
      delete
      createVersion
      createTemplateVersion
    }
    webhookUrl
    webhookEnabled
    id
    createdAt
    code
    name
    description
    schedule
    type
    notebookPath
    sourceTemplate {
      id
      code
      name
    }
    hasNewTemplateVersions
    newTemplateVersions {
      id
      changelog
      versionNumber
      createdAt
    }
    currentVersion {
      id
      versionName
      description
      config
      externalLink
      ...PipelineVersionParametersTable_version
      ...PipelineVersionConfigDialog_version
    }
    recipients {
      user {
        id
        displayName
      }
    }
  }
}
    ${PipelineLayout_WorkspaceFragmentDoc}
${RunPipelineDialog_PipelineFragmentDoc}
${PipelineLayout_PipelineFragmentDoc}
${PipelineVersionParametersTable_VersionFragmentDoc}
${PipelineVersionConfigDialog_VersionFragmentDoc}`;

/**
 * __useWorkspacePipelinePageQuery__
 *
 * To run a query within a React component, call `useWorkspacePipelinePageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspacePipelinePageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspacePipelinePageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      pipelineCode: // value for 'pipelineCode'
 *   },
 * });
 */
export function useWorkspacePipelinePageQuery(baseOptions: Apollo.QueryHookOptions<WorkspacePipelinePageQuery, WorkspacePipelinePageQueryVariables> & ({ variables: WorkspacePipelinePageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspacePipelinePageQuery, WorkspacePipelinePageQueryVariables>(WorkspacePipelinePageDocument, options);
      }
export function useWorkspacePipelinePageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspacePipelinePageQuery, WorkspacePipelinePageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspacePipelinePageQuery, WorkspacePipelinePageQueryVariables>(WorkspacePipelinePageDocument, options);
        }
export function useWorkspacePipelinePageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspacePipelinePageQuery, WorkspacePipelinePageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspacePipelinePageQuery, WorkspacePipelinePageQueryVariables>(WorkspacePipelinePageDocument, options);
        }
export type WorkspacePipelinePageQueryHookResult = ReturnType<typeof useWorkspacePipelinePageQuery>;
export type WorkspacePipelinePageLazyQueryHookResult = ReturnType<typeof useWorkspacePipelinePageLazyQuery>;
export type WorkspacePipelinePageSuspenseQueryHookResult = ReturnType<typeof useWorkspacePipelinePageSuspenseQuery>;
export type WorkspacePipelinePageQueryResult = Apollo.QueryResult<WorkspacePipelinePageQuery, WorkspacePipelinePageQueryVariables>;
export const WorkspacePipelineRunsPageDocument = gql`
    query WorkspacePipelineRunsPage($workspaceSlug: String!, $pipelineCode: String!, $page: Int = 1, $perPage: Int = 10) {
  workspace(slug: $workspaceSlug) {
    slug
    name
    ...PipelineLayout_workspace
  }
  pipeline: pipelineByCode(workspaceSlug: $workspaceSlug, code: $pipelineCode) {
    ...PipelineLayout_pipeline
    id
    type
    runs(page: $page, perPage: $perPage) {
      items {
        id
        version {
          versionName
          createdAt
          user {
            ...User_user
          }
        }
        executionDate
        duration
        triggerMode
        user {
          ...UserColumn_user
        }
        ...PipelineRunStatusBadge_run
      }
      totalItems
      totalPages
      pageNumber
    }
  }
}
    ${PipelineLayout_WorkspaceFragmentDoc}
${PipelineLayout_PipelineFragmentDoc}
${User_UserFragmentDoc}
${UserColumn_UserFragmentDoc}
${PipelineRunStatusBadge_RunFragmentDoc}`;

/**
 * __useWorkspacePipelineRunsPageQuery__
 *
 * To run a query within a React component, call `useWorkspacePipelineRunsPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspacePipelineRunsPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspacePipelineRunsPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      pipelineCode: // value for 'pipelineCode'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useWorkspacePipelineRunsPageQuery(baseOptions: Apollo.QueryHookOptions<WorkspacePipelineRunsPageQuery, WorkspacePipelineRunsPageQueryVariables> & ({ variables: WorkspacePipelineRunsPageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspacePipelineRunsPageQuery, WorkspacePipelineRunsPageQueryVariables>(WorkspacePipelineRunsPageDocument, options);
      }
export function useWorkspacePipelineRunsPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspacePipelineRunsPageQuery, WorkspacePipelineRunsPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspacePipelineRunsPageQuery, WorkspacePipelineRunsPageQueryVariables>(WorkspacePipelineRunsPageDocument, options);
        }
export function useWorkspacePipelineRunsPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspacePipelineRunsPageQuery, WorkspacePipelineRunsPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspacePipelineRunsPageQuery, WorkspacePipelineRunsPageQueryVariables>(WorkspacePipelineRunsPageDocument, options);
        }
export type WorkspacePipelineRunsPageQueryHookResult = ReturnType<typeof useWorkspacePipelineRunsPageQuery>;
export type WorkspacePipelineRunsPageLazyQueryHookResult = ReturnType<typeof useWorkspacePipelineRunsPageLazyQuery>;
export type WorkspacePipelineRunsPageSuspenseQueryHookResult = ReturnType<typeof useWorkspacePipelineRunsPageSuspenseQuery>;
export type WorkspacePipelineRunsPageQueryResult = Apollo.QueryResult<WorkspacePipelineRunsPageQuery, WorkspacePipelineRunsPageQueryVariables>;
export const WorkspacePipelineNotificationsPageDocument = gql`
    query WorkspacePipelineNotificationsPage($workspaceSlug: String!, $pipelineCode: String!) {
  workspace(slug: $workspaceSlug) {
    ...PipelineLayout_workspace
  }
  pipeline: pipelineByCode(workspaceSlug: $workspaceSlug, code: $pipelineCode) {
    ...PipelineLayout_pipeline
    ...PipelineRecipients_pipeline
    id
    code
    type
    schedule
    permissions {
      schedule
      update
    }
  }
}
    ${PipelineLayout_WorkspaceFragmentDoc}
${PipelineLayout_PipelineFragmentDoc}
${PipelineRecipients_PipelineFragmentDoc}`;

/**
 * __useWorkspacePipelineNotificationsPageQuery__
 *
 * To run a query within a React component, call `useWorkspacePipelineNotificationsPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspacePipelineNotificationsPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspacePipelineNotificationsPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      pipelineCode: // value for 'pipelineCode'
 *   },
 * });
 */
export function useWorkspacePipelineNotificationsPageQuery(baseOptions: Apollo.QueryHookOptions<WorkspacePipelineNotificationsPageQuery, WorkspacePipelineNotificationsPageQueryVariables> & ({ variables: WorkspacePipelineNotificationsPageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspacePipelineNotificationsPageQuery, WorkspacePipelineNotificationsPageQueryVariables>(WorkspacePipelineNotificationsPageDocument, options);
      }
export function useWorkspacePipelineNotificationsPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspacePipelineNotificationsPageQuery, WorkspacePipelineNotificationsPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspacePipelineNotificationsPageQuery, WorkspacePipelineNotificationsPageQueryVariables>(WorkspacePipelineNotificationsPageDocument, options);
        }
export function useWorkspacePipelineNotificationsPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspacePipelineNotificationsPageQuery, WorkspacePipelineNotificationsPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspacePipelineNotificationsPageQuery, WorkspacePipelineNotificationsPageQueryVariables>(WorkspacePipelineNotificationsPageDocument, options);
        }
export type WorkspacePipelineNotificationsPageQueryHookResult = ReturnType<typeof useWorkspacePipelineNotificationsPageQuery>;
export type WorkspacePipelineNotificationsPageLazyQueryHookResult = ReturnType<typeof useWorkspacePipelineNotificationsPageLazyQuery>;
export type WorkspacePipelineNotificationsPageSuspenseQueryHookResult = ReturnType<typeof useWorkspacePipelineNotificationsPageSuspenseQuery>;
export type WorkspacePipelineNotificationsPageQueryResult = Apollo.QueryResult<WorkspacePipelineNotificationsPageQuery, WorkspacePipelineNotificationsPageQueryVariables>;
export const WorkspacePipelineVersionsPageDocument = gql`
    query WorkspacePipelineVersionsPage($workspaceSlug: String!, $pipelineCode: String!, $page: Int!, $perPage: Int!) {
  workspace(slug: $workspaceSlug) {
    slug
    name
    ...WorkspaceLayout_workspace
  }
  pipeline: pipelineByCode(workspaceSlug: $workspaceSlug, code: $pipelineCode) {
    id
    code
    name
    currentVersion {
      id
    }
    versions(page: $page, perPage: $perPage) {
      items {
        ...PipelineVersionCard_version
        id
      }
      totalItems
      totalPages
    }
  }
}
    ${WorkspaceLayout_WorkspaceFragmentDoc}
${PipelineVersionCard_VersionFragmentDoc}`;

/**
 * __useWorkspacePipelineVersionsPageQuery__
 *
 * To run a query within a React component, call `useWorkspacePipelineVersionsPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspacePipelineVersionsPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspacePipelineVersionsPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      pipelineCode: // value for 'pipelineCode'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useWorkspacePipelineVersionsPageQuery(baseOptions: Apollo.QueryHookOptions<WorkspacePipelineVersionsPageQuery, WorkspacePipelineVersionsPageQueryVariables> & ({ variables: WorkspacePipelineVersionsPageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspacePipelineVersionsPageQuery, WorkspacePipelineVersionsPageQueryVariables>(WorkspacePipelineVersionsPageDocument, options);
      }
export function useWorkspacePipelineVersionsPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspacePipelineVersionsPageQuery, WorkspacePipelineVersionsPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspacePipelineVersionsPageQuery, WorkspacePipelineVersionsPageQueryVariables>(WorkspacePipelineVersionsPageDocument, options);
        }
export function useWorkspacePipelineVersionsPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspacePipelineVersionsPageQuery, WorkspacePipelineVersionsPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspacePipelineVersionsPageQuery, WorkspacePipelineVersionsPageQueryVariables>(WorkspacePipelineVersionsPageDocument, options);
        }
export type WorkspacePipelineVersionsPageQueryHookResult = ReturnType<typeof useWorkspacePipelineVersionsPageQuery>;
export type WorkspacePipelineVersionsPageLazyQueryHookResult = ReturnType<typeof useWorkspacePipelineVersionsPageLazyQuery>;
export type WorkspacePipelineVersionsPageSuspenseQueryHookResult = ReturnType<typeof useWorkspacePipelineVersionsPageSuspenseQuery>;
export type WorkspacePipelineVersionsPageQueryResult = Apollo.QueryResult<WorkspacePipelineVersionsPageQuery, WorkspacePipelineVersionsPageQueryVariables>;
export const WorkspacePipelineStartPageDocument = gql`
    query WorkspacePipelineStartPage($workspaceSlug: String!) {
  workspace(slug: $workspaceSlug) {
    slug
    name
    ...WorkspaceLayout_workspace
  }
}
    ${WorkspaceLayout_WorkspaceFragmentDoc}`;

/**
 * __useWorkspacePipelineStartPageQuery__
 *
 * To run a query within a React component, call `useWorkspacePipelineStartPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspacePipelineStartPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspacePipelineStartPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *   },
 * });
 */
export function useWorkspacePipelineStartPageQuery(baseOptions: Apollo.QueryHookOptions<WorkspacePipelineStartPageQuery, WorkspacePipelineStartPageQueryVariables> & ({ variables: WorkspacePipelineStartPageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspacePipelineStartPageQuery, WorkspacePipelineStartPageQueryVariables>(WorkspacePipelineStartPageDocument, options);
      }
export function useWorkspacePipelineStartPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspacePipelineStartPageQuery, WorkspacePipelineStartPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspacePipelineStartPageQuery, WorkspacePipelineStartPageQueryVariables>(WorkspacePipelineStartPageDocument, options);
        }
export function useWorkspacePipelineStartPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspacePipelineStartPageQuery, WorkspacePipelineStartPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspacePipelineStartPageQuery, WorkspacePipelineStartPageQueryVariables>(WorkspacePipelineStartPageDocument, options);
        }
export type WorkspacePipelineStartPageQueryHookResult = ReturnType<typeof useWorkspacePipelineStartPageQuery>;
export type WorkspacePipelineStartPageLazyQueryHookResult = ReturnType<typeof useWorkspacePipelineStartPageLazyQuery>;
export type WorkspacePipelineStartPageSuspenseQueryHookResult = ReturnType<typeof useWorkspacePipelineStartPageSuspenseQuery>;
export type WorkspacePipelineStartPageQueryResult = Apollo.QueryResult<WorkspacePipelineStartPageQuery, WorkspacePipelineStartPageQueryVariables>;
export const WorkspacePipelineRunPageDocument = gql`
    query WorkspacePipelineRunPage($workspaceSlug: String!, $runId: UUID!) {
  workspace(slug: $workspaceSlug) {
    slug
    name
    ...WorkspaceLayout_workspace
    ...RunOutputsTable_workspace
  }
  pipelineRun(id: $runId) {
    id
    version {
      versionName
      parameters {
        code
        name
        help
        type
        default
        required
        choices
        multiple
      }
    }
    timeout
    config
    executionDate
    duration
    triggerMode
    pipeline {
      id
      code
      name
      type
      notebookPath
      permissions {
        stopPipeline
      }
      ...RunPipelineDialog_pipeline
    }
    user {
      ...User_user
    }
    stoppedBy {
      ...User_user
    }
    ...RunOutputsTable_run
    ...RunPipelineDialog_run
    ...RunMessages_run
    ...RunLogs_run
    ...PipelineRunStatusBadge_run
  }
}
    ${WorkspaceLayout_WorkspaceFragmentDoc}
${RunOutputsTable_WorkspaceFragmentDoc}
${RunPipelineDialog_PipelineFragmentDoc}
${User_UserFragmentDoc}
${RunOutputsTable_RunFragmentDoc}
${RunPipelineDialog_RunFragmentDoc}
${RunMessages_RunFragmentDoc}
${RunLogs_RunFragmentDoc}
${PipelineRunStatusBadge_RunFragmentDoc}`;

/**
 * __useWorkspacePipelineRunPageQuery__
 *
 * To run a query within a React component, call `useWorkspacePipelineRunPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspacePipelineRunPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspacePipelineRunPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      runId: // value for 'runId'
 *   },
 * });
 */
export function useWorkspacePipelineRunPageQuery(baseOptions: Apollo.QueryHookOptions<WorkspacePipelineRunPageQuery, WorkspacePipelineRunPageQueryVariables> & ({ variables: WorkspacePipelineRunPageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspacePipelineRunPageQuery, WorkspacePipelineRunPageQueryVariables>(WorkspacePipelineRunPageDocument, options);
      }
export function useWorkspacePipelineRunPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspacePipelineRunPageQuery, WorkspacePipelineRunPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspacePipelineRunPageQuery, WorkspacePipelineRunPageQueryVariables>(WorkspacePipelineRunPageDocument, options);
        }
export function useWorkspacePipelineRunPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspacePipelineRunPageQuery, WorkspacePipelineRunPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspacePipelineRunPageQuery, WorkspacePipelineRunPageQueryVariables>(WorkspacePipelineRunPageDocument, options);
        }
export type WorkspacePipelineRunPageQueryHookResult = ReturnType<typeof useWorkspacePipelineRunPageQuery>;
export type WorkspacePipelineRunPageLazyQueryHookResult = ReturnType<typeof useWorkspacePipelineRunPageLazyQuery>;
export type WorkspacePipelineRunPageSuspenseQueryHookResult = ReturnType<typeof useWorkspacePipelineRunPageSuspenseQuery>;
export type WorkspacePipelineRunPageQueryResult = Apollo.QueryResult<WorkspacePipelineRunPageQuery, WorkspacePipelineRunPageQueryVariables>;
export const WorkspaceDatasetsPageDocument = gql`
    query WorkspaceDatasetsPage($workspaceSlug: String!, $page: Int, $perPage: Int, $query: String) {
  workspace(slug: $workspaceSlug) {
    slug
    name
    ...WorkspaceLayout_workspace
    ...CreateDatasetDialog_workspace
    permissions {
      createDataset
    }
    pinnedDatasets: datasets(pinned: true, page: 1, perPage: 6) {
      items {
        ...DatasetCard_link
      }
    }
    datasets(query: $query, page: $page, perPage: $perPage) {
      items {
        ...PinDatasetButton_link
        id
        dataset {
          id
          name
          slug
          description
          updatedAt
          workspace {
            slug
            name
          }
          permissions {
            update
            delete
          }
          createdBy {
            ...User_user
          }
        }
      }
      totalItems
      totalPages
      pageNumber
    }
  }
}
    ${WorkspaceLayout_WorkspaceFragmentDoc}
${CreateDatasetDialog_WorkspaceFragmentDoc}
${DatasetCard_LinkFragmentDoc}
${PinDatasetButton_LinkFragmentDoc}
${User_UserFragmentDoc}`;

/**
 * __useWorkspaceDatasetsPageQuery__
 *
 * To run a query within a React component, call `useWorkspaceDatasetsPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspaceDatasetsPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspaceDatasetsPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *      query: // value for 'query'
 *   },
 * });
 */
export function useWorkspaceDatasetsPageQuery(baseOptions: Apollo.QueryHookOptions<WorkspaceDatasetsPageQuery, WorkspaceDatasetsPageQueryVariables> & ({ variables: WorkspaceDatasetsPageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspaceDatasetsPageQuery, WorkspaceDatasetsPageQueryVariables>(WorkspaceDatasetsPageDocument, options);
      }
export function useWorkspaceDatasetsPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspaceDatasetsPageQuery, WorkspaceDatasetsPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspaceDatasetsPageQuery, WorkspaceDatasetsPageQueryVariables>(WorkspaceDatasetsPageDocument, options);
        }
export function useWorkspaceDatasetsPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspaceDatasetsPageQuery, WorkspaceDatasetsPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspaceDatasetsPageQuery, WorkspaceDatasetsPageQueryVariables>(WorkspaceDatasetsPageDocument, options);
        }
export type WorkspaceDatasetsPageQueryHookResult = ReturnType<typeof useWorkspaceDatasetsPageQuery>;
export type WorkspaceDatasetsPageLazyQueryHookResult = ReturnType<typeof useWorkspaceDatasetsPageLazyQuery>;
export type WorkspaceDatasetsPageSuspenseQueryHookResult = ReturnType<typeof useWorkspaceDatasetsPageSuspenseQuery>;
export type WorkspaceDatasetsPageQueryResult = Apollo.QueryResult<WorkspaceDatasetsPageQuery, WorkspaceDatasetsPageQueryVariables>;
export const WorkspaceDatasetIndexPageDocument = gql`
    query WorkspaceDatasetIndexPage($workspaceSlug: String!, $datasetSlug: String!, $versionId: ID!, $isSpecificVersion: Boolean!) {
  workspace(slug: $workspaceSlug) {
    slug
    ...DatasetLayout_workspace
  }
  datasetLink: datasetLinkBySlug(
    workspaceSlug: $workspaceSlug
    datasetSlug: $datasetSlug
  ) {
    ...DatasetLayout_datasetLink
    id
    dataset {
      permissions {
        update
      }
      description
      updatedAt
      createdAt
      workspace {
        name
        slug
      }
      createdBy {
        ...User_user
      }
      version(id: $versionId) @include(if: $isSpecificVersion) {
        id
        createdAt
        changelog
        createdBy {
          ...User_user
        }
        permissions {
          update
        }
        name
        ...DatasetLayout_version
      }
      latestVersion @skip(if: $isSpecificVersion) {
        id
        changelog
        createdAt
        createdBy {
          ...User_user
        }
        permissions {
          update
        }
        name
        ...DatasetLayout_version
      }
    }
  }
}
    ${DatasetLayout_WorkspaceFragmentDoc}
${DatasetLayout_DatasetLinkFragmentDoc}
${User_UserFragmentDoc}
${DatasetLayout_VersionFragmentDoc}`;

/**
 * __useWorkspaceDatasetIndexPageQuery__
 *
 * To run a query within a React component, call `useWorkspaceDatasetIndexPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspaceDatasetIndexPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspaceDatasetIndexPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      datasetSlug: // value for 'datasetSlug'
 *      versionId: // value for 'versionId'
 *      isSpecificVersion: // value for 'isSpecificVersion'
 *   },
 * });
 */
export function useWorkspaceDatasetIndexPageQuery(baseOptions: Apollo.QueryHookOptions<WorkspaceDatasetIndexPageQuery, WorkspaceDatasetIndexPageQueryVariables> & ({ variables: WorkspaceDatasetIndexPageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspaceDatasetIndexPageQuery, WorkspaceDatasetIndexPageQueryVariables>(WorkspaceDatasetIndexPageDocument, options);
      }
export function useWorkspaceDatasetIndexPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspaceDatasetIndexPageQuery, WorkspaceDatasetIndexPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspaceDatasetIndexPageQuery, WorkspaceDatasetIndexPageQueryVariables>(WorkspaceDatasetIndexPageDocument, options);
        }
export function useWorkspaceDatasetIndexPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspaceDatasetIndexPageQuery, WorkspaceDatasetIndexPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspaceDatasetIndexPageQuery, WorkspaceDatasetIndexPageQueryVariables>(WorkspaceDatasetIndexPageDocument, options);
        }
export type WorkspaceDatasetIndexPageQueryHookResult = ReturnType<typeof useWorkspaceDatasetIndexPageQuery>;
export type WorkspaceDatasetIndexPageLazyQueryHookResult = ReturnType<typeof useWorkspaceDatasetIndexPageLazyQuery>;
export type WorkspaceDatasetIndexPageSuspenseQueryHookResult = ReturnType<typeof useWorkspaceDatasetIndexPageSuspenseQuery>;
export type WorkspaceDatasetIndexPageQueryResult = Apollo.QueryResult<WorkspaceDatasetIndexPageQuery, WorkspaceDatasetIndexPageQueryVariables>;
export const WorkspaceDatasetAccessPageDocument = gql`
    query WorkspaceDatasetAccessPage($workspaceSlug: String!, $datasetSlug: String!, $versionId: ID!, $isSpecificVersion: Boolean!) {
  workspace(slug: $workspaceSlug) {
    slug
    ...DatasetLayout_workspace
  }
  datasetLink: datasetLinkBySlug(
    workspaceSlug: $workspaceSlug
    datasetSlug: $datasetSlug
  ) {
    ...DatasetLayout_datasetLink
    id
    dataset {
      name
      permissions {
        update
      }
      ...DatasetLinksDataGrid_dataset
      version(id: $versionId) @include(if: $isSpecificVersion) {
        ...DatasetLayout_version
      }
      latestVersion @skip(if: $isSpecificVersion) {
        ...DatasetLayout_version
      }
    }
  }
}
    ${DatasetLayout_WorkspaceFragmentDoc}
${DatasetLayout_DatasetLinkFragmentDoc}
${DatasetLinksDataGrid_DatasetFragmentDoc}
${DatasetLayout_VersionFragmentDoc}`;

/**
 * __useWorkspaceDatasetAccessPageQuery__
 *
 * To run a query within a React component, call `useWorkspaceDatasetAccessPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspaceDatasetAccessPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspaceDatasetAccessPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      datasetSlug: // value for 'datasetSlug'
 *      versionId: // value for 'versionId'
 *      isSpecificVersion: // value for 'isSpecificVersion'
 *   },
 * });
 */
export function useWorkspaceDatasetAccessPageQuery(baseOptions: Apollo.QueryHookOptions<WorkspaceDatasetAccessPageQuery, WorkspaceDatasetAccessPageQueryVariables> & ({ variables: WorkspaceDatasetAccessPageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspaceDatasetAccessPageQuery, WorkspaceDatasetAccessPageQueryVariables>(WorkspaceDatasetAccessPageDocument, options);
      }
export function useWorkspaceDatasetAccessPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspaceDatasetAccessPageQuery, WorkspaceDatasetAccessPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspaceDatasetAccessPageQuery, WorkspaceDatasetAccessPageQueryVariables>(WorkspaceDatasetAccessPageDocument, options);
        }
export function useWorkspaceDatasetAccessPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspaceDatasetAccessPageQuery, WorkspaceDatasetAccessPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspaceDatasetAccessPageQuery, WorkspaceDatasetAccessPageQueryVariables>(WorkspaceDatasetAccessPageDocument, options);
        }
export type WorkspaceDatasetAccessPageQueryHookResult = ReturnType<typeof useWorkspaceDatasetAccessPageQuery>;
export type WorkspaceDatasetAccessPageLazyQueryHookResult = ReturnType<typeof useWorkspaceDatasetAccessPageLazyQuery>;
export type WorkspaceDatasetAccessPageSuspenseQueryHookResult = ReturnType<typeof useWorkspaceDatasetAccessPageSuspenseQuery>;
export type WorkspaceDatasetAccessPageQueryResult = Apollo.QueryResult<WorkspaceDatasetAccessPageQuery, WorkspaceDatasetAccessPageQueryVariables>;
export const WorkspaceDatasetFilesPageDocument = gql`
    query WorkspaceDatasetFilesPage($workspaceSlug: String!, $datasetSlug: String!, $versionId: ID!, $isSpecificVersion: Boolean!) {
  workspace(slug: $workspaceSlug) {
    slug
    ...DatasetLayout_workspace
  }
  datasetLink: datasetLinkBySlug(
    workspaceSlug: $workspaceSlug
    datasetSlug: $datasetSlug
  ) {
    ...DatasetLayout_datasetLink
    id
    dataset {
      name
      ...DatasetLinksDataGrid_dataset
      version(id: $versionId) @include(if: $isSpecificVersion) {
        ...DatasetLayout_version
        ...DatasetExplorer_version
      }
      latestVersion @skip(if: $isSpecificVersion) {
        ...DatasetLayout_version
        ...DatasetExplorer_version
      }
    }
  }
}
    ${DatasetLayout_WorkspaceFragmentDoc}
${DatasetLayout_DatasetLinkFragmentDoc}
${DatasetLinksDataGrid_DatasetFragmentDoc}
${DatasetLayout_VersionFragmentDoc}
${DatasetExplorer_VersionFragmentDoc}`;

/**
 * __useWorkspaceDatasetFilesPageQuery__
 *
 * To run a query within a React component, call `useWorkspaceDatasetFilesPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspaceDatasetFilesPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspaceDatasetFilesPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      datasetSlug: // value for 'datasetSlug'
 *      versionId: // value for 'versionId'
 *      isSpecificVersion: // value for 'isSpecificVersion'
 *   },
 * });
 */
export function useWorkspaceDatasetFilesPageQuery(baseOptions: Apollo.QueryHookOptions<WorkspaceDatasetFilesPageQuery, WorkspaceDatasetFilesPageQueryVariables> & ({ variables: WorkspaceDatasetFilesPageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspaceDatasetFilesPageQuery, WorkspaceDatasetFilesPageQueryVariables>(WorkspaceDatasetFilesPageDocument, options);
      }
export function useWorkspaceDatasetFilesPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspaceDatasetFilesPageQuery, WorkspaceDatasetFilesPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspaceDatasetFilesPageQuery, WorkspaceDatasetFilesPageQueryVariables>(WorkspaceDatasetFilesPageDocument, options);
        }
export function useWorkspaceDatasetFilesPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspaceDatasetFilesPageQuery, WorkspaceDatasetFilesPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspaceDatasetFilesPageQuery, WorkspaceDatasetFilesPageQueryVariables>(WorkspaceDatasetFilesPageDocument, options);
        }
export type WorkspaceDatasetFilesPageQueryHookResult = ReturnType<typeof useWorkspaceDatasetFilesPageQuery>;
export type WorkspaceDatasetFilesPageLazyQueryHookResult = ReturnType<typeof useWorkspaceDatasetFilesPageLazyQuery>;
export type WorkspaceDatasetFilesPageSuspenseQueryHookResult = ReturnType<typeof useWorkspaceDatasetFilesPageSuspenseQuery>;
export type WorkspaceDatasetFilesPageQueryResult = Apollo.QueryResult<WorkspaceDatasetFilesPageQuery, WorkspaceDatasetFilesPageQueryVariables>;
export const WorkspaceFilesPageDocument = gql`
    query WorkspaceFilesPage($workspaceSlug: String!, $page: Int!, $perPage: Int!, $prefix: String!, $query: String, $ignoreHiddenFiles: Boolean) {
  workspace(slug: $workspaceSlug) {
    slug
    name
    ...BucketExplorer_workspace
    ...WorkspaceLayout_workspace
    ...UploadObjectDialog_workspace
    ...CreateBucketFolderDialog_workspace
    ...BucketExplorer_workspace
    bucket {
      objects(
        page: $page
        prefix: $prefix
        perPage: $perPage
        query: $query
        ignoreHiddenFiles: $ignoreHiddenFiles
      ) {
        ...BucketExplorer_objects
      }
    }
    permissions {
      createObject
    }
  }
}
    ${BucketExplorer_WorkspaceFragmentDoc}
${WorkspaceLayout_WorkspaceFragmentDoc}
${UploadObjectDialog_WorkspaceFragmentDoc}
${CreateBucketFolderDialog_WorkspaceFragmentDoc}
${BucketExplorer_ObjectsFragmentDoc}`;

/**
 * __useWorkspaceFilesPageQuery__
 *
 * To run a query within a React component, call `useWorkspaceFilesPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspaceFilesPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspaceFilesPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *      prefix: // value for 'prefix'
 *      query: // value for 'query'
 *      ignoreHiddenFiles: // value for 'ignoreHiddenFiles'
 *   },
 * });
 */
export function useWorkspaceFilesPageQuery(baseOptions: Apollo.QueryHookOptions<WorkspaceFilesPageQuery, WorkspaceFilesPageQueryVariables> & ({ variables: WorkspaceFilesPageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspaceFilesPageQuery, WorkspaceFilesPageQueryVariables>(WorkspaceFilesPageDocument, options);
      }
export function useWorkspaceFilesPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspaceFilesPageQuery, WorkspaceFilesPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspaceFilesPageQuery, WorkspaceFilesPageQueryVariables>(WorkspaceFilesPageDocument, options);
        }
export function useWorkspaceFilesPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspaceFilesPageQuery, WorkspaceFilesPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspaceFilesPageQuery, WorkspaceFilesPageQueryVariables>(WorkspaceFilesPageDocument, options);
        }
export type WorkspaceFilesPageQueryHookResult = ReturnType<typeof useWorkspaceFilesPageQuery>;
export type WorkspaceFilesPageLazyQueryHookResult = ReturnType<typeof useWorkspaceFilesPageLazyQuery>;
export type WorkspaceFilesPageSuspenseQueryHookResult = ReturnType<typeof useWorkspaceFilesPageSuspenseQuery>;
export type WorkspaceFilesPageQueryResult = Apollo.QueryResult<WorkspaceFilesPageQuery, WorkspaceFilesPageQueryVariables>;
export const WorkspaceDatabasesPageDocument = gql`
    query WorkspaceDatabasesPage($workspaceSlug: String!, $page: Int, $perPage: Int) {
  workspace(slug: $workspaceSlug) {
    slug
    name
    permissions {
      update
    }
    database {
      tables(page: $page, perPage: $perPage) {
        totalPages
        totalItems
        items {
          name
          count
        }
      }
    }
    ...DatabaseVariablesSection_workspace
    ...WorkspaceLayout_workspace
  }
}
    ${DatabaseVariablesSection_WorkspaceFragmentDoc}
${WorkspaceLayout_WorkspaceFragmentDoc}`;

/**
 * __useWorkspaceDatabasesPageQuery__
 *
 * To run a query within a React component, call `useWorkspaceDatabasesPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspaceDatabasesPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspaceDatabasesPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useWorkspaceDatabasesPageQuery(baseOptions: Apollo.QueryHookOptions<WorkspaceDatabasesPageQuery, WorkspaceDatabasesPageQueryVariables> & ({ variables: WorkspaceDatabasesPageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspaceDatabasesPageQuery, WorkspaceDatabasesPageQueryVariables>(WorkspaceDatabasesPageDocument, options);
      }
export function useWorkspaceDatabasesPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspaceDatabasesPageQuery, WorkspaceDatabasesPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspaceDatabasesPageQuery, WorkspaceDatabasesPageQueryVariables>(WorkspaceDatabasesPageDocument, options);
        }
export function useWorkspaceDatabasesPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspaceDatabasesPageQuery, WorkspaceDatabasesPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspaceDatabasesPageQuery, WorkspaceDatabasesPageQueryVariables>(WorkspaceDatabasesPageDocument, options);
        }
export type WorkspaceDatabasesPageQueryHookResult = ReturnType<typeof useWorkspaceDatabasesPageQuery>;
export type WorkspaceDatabasesPageLazyQueryHookResult = ReturnType<typeof useWorkspaceDatabasesPageLazyQuery>;
export type WorkspaceDatabasesPageSuspenseQueryHookResult = ReturnType<typeof useWorkspaceDatabasesPageSuspenseQuery>;
export type WorkspaceDatabasesPageQueryResult = Apollo.QueryResult<WorkspaceDatabasesPageQuery, WorkspaceDatabasesPageQueryVariables>;
export const WorkspaceDatabaseTablePageDocument = gql`
    query WorkspaceDatabaseTablePage($workspaceSlug: String!, $tableName: String!) {
  workspace(slug: $workspaceSlug) {
    slug
    name
    permissions {
      deleteDatabaseTable
    }
    database {
      table(name: $tableName) {
        name
        count
        columns {
          name
          type
        }
        ...DatabaseTableDataGrid_table
      }
    }
    ...DatabaseTableDataGrid_workspace
    ...WorkspaceLayout_workspace
  }
}
    ${DatabaseTableDataGrid_TableFragmentDoc}
${DatabaseTableDataGrid_WorkspaceFragmentDoc}
${WorkspaceLayout_WorkspaceFragmentDoc}`;

/**
 * __useWorkspaceDatabaseTablePageQuery__
 *
 * To run a query within a React component, call `useWorkspaceDatabaseTablePageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspaceDatabaseTablePageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspaceDatabaseTablePageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      tableName: // value for 'tableName'
 *   },
 * });
 */
export function useWorkspaceDatabaseTablePageQuery(baseOptions: Apollo.QueryHookOptions<WorkspaceDatabaseTablePageQuery, WorkspaceDatabaseTablePageQueryVariables> & ({ variables: WorkspaceDatabaseTablePageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspaceDatabaseTablePageQuery, WorkspaceDatabaseTablePageQueryVariables>(WorkspaceDatabaseTablePageDocument, options);
      }
export function useWorkspaceDatabaseTablePageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspaceDatabaseTablePageQuery, WorkspaceDatabaseTablePageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspaceDatabaseTablePageQuery, WorkspaceDatabaseTablePageQueryVariables>(WorkspaceDatabaseTablePageDocument, options);
        }
export function useWorkspaceDatabaseTablePageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspaceDatabaseTablePageQuery, WorkspaceDatabaseTablePageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspaceDatabaseTablePageQuery, WorkspaceDatabaseTablePageQueryVariables>(WorkspaceDatabaseTablePageDocument, options);
        }
export type WorkspaceDatabaseTablePageQueryHookResult = ReturnType<typeof useWorkspaceDatabaseTablePageQuery>;
export type WorkspaceDatabaseTablePageLazyQueryHookResult = ReturnType<typeof useWorkspaceDatabaseTablePageLazyQuery>;
export type WorkspaceDatabaseTablePageSuspenseQueryHookResult = ReturnType<typeof useWorkspaceDatabaseTablePageSuspenseQuery>;
export type WorkspaceDatabaseTablePageQueryResult = Apollo.QueryResult<WorkspaceDatabaseTablePageQuery, WorkspaceDatabaseTablePageQueryVariables>;
export const ConnectionsPageDocument = gql`
    query ConnectionsPage($workspaceSlug: String!) {
  workspace(slug: $workspaceSlug) {
    slug
    name
    permissions {
      update
      createConnection
    }
    ...CreateConnectionDialog_workspace
    connections {
      id
      description
      name
      type
      slug
      updatedAt
      permissions {
        update
        delete
      }
    }
    ...WorkspaceLayout_workspace
  }
}
    ${CreateConnectionDialog_WorkspaceFragmentDoc}
${WorkspaceLayout_WorkspaceFragmentDoc}`;

/**
 * __useConnectionsPageQuery__
 *
 * To run a query within a React component, call `useConnectionsPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useConnectionsPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useConnectionsPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *   },
 * });
 */
export function useConnectionsPageQuery(baseOptions: Apollo.QueryHookOptions<ConnectionsPageQuery, ConnectionsPageQueryVariables> & ({ variables: ConnectionsPageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<ConnectionsPageQuery, ConnectionsPageQueryVariables>(ConnectionsPageDocument, options);
      }
export function useConnectionsPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<ConnectionsPageQuery, ConnectionsPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<ConnectionsPageQuery, ConnectionsPageQueryVariables>(ConnectionsPageDocument, options);
        }
export function useConnectionsPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<ConnectionsPageQuery, ConnectionsPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<ConnectionsPageQuery, ConnectionsPageQueryVariables>(ConnectionsPageDocument, options);
        }
export type ConnectionsPageQueryHookResult = ReturnType<typeof useConnectionsPageQuery>;
export type ConnectionsPageLazyQueryHookResult = ReturnType<typeof useConnectionsPageLazyQuery>;
export type ConnectionsPageSuspenseQueryHookResult = ReturnType<typeof useConnectionsPageSuspenseQuery>;
export type ConnectionsPageQueryResult = Apollo.QueryResult<ConnectionsPageQuery, ConnectionsPageQueryVariables>;
export const ConnectionPageDocument = gql`
    query ConnectionPage($workspaceSlug: String!, $connectionId: UUID!) {
  workspace(slug: $workspaceSlug) {
    slug
    name
    permissions {
      update
    }
    ...WorkspaceLayout_workspace
  }
  connection(id: $connectionId) {
    id
    name
    slug
    description
    type
    createdAt
    permissions {
      update
      delete
    }
    ...ConnectionUsageSnippets_connection
    ...ConnectionFieldsSection_connection
  }
}
    ${WorkspaceLayout_WorkspaceFragmentDoc}
${ConnectionUsageSnippets_ConnectionFragmentDoc}
${ConnectionFieldsSection_ConnectionFragmentDoc}`;

/**
 * __useConnectionPageQuery__
 *
 * To run a query within a React component, call `useConnectionPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useConnectionPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useConnectionPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      connectionId: // value for 'connectionId'
 *   },
 * });
 */
export function useConnectionPageQuery(baseOptions: Apollo.QueryHookOptions<ConnectionPageQuery, ConnectionPageQueryVariables> & ({ variables: ConnectionPageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<ConnectionPageQuery, ConnectionPageQueryVariables>(ConnectionPageDocument, options);
      }
export function useConnectionPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<ConnectionPageQuery, ConnectionPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<ConnectionPageQuery, ConnectionPageQueryVariables>(ConnectionPageDocument, options);
        }
export function useConnectionPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<ConnectionPageQuery, ConnectionPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<ConnectionPageQuery, ConnectionPageQueryVariables>(ConnectionPageDocument, options);
        }
export type ConnectionPageQueryHookResult = ReturnType<typeof useConnectionPageQuery>;
export type ConnectionPageLazyQueryHookResult = ReturnType<typeof useConnectionPageLazyQuery>;
export type ConnectionPageSuspenseQueryHookResult = ReturnType<typeof useConnectionPageSuspenseQuery>;
export type ConnectionPageQueryResult = Apollo.QueryResult<ConnectionPageQuery, ConnectionPageQueryVariables>;
export const CheckWorkspaceAvailabilityDocument = gql`
    query CheckWorkspaceAvailability($slug: String!) {
  workspace(slug: $slug) {
    slug
  }
}
    `;

/**
 * __useCheckWorkspaceAvailabilityQuery__
 *
 * To run a query within a React component, call `useCheckWorkspaceAvailabilityQuery` and pass it any options that fit your needs.
 * When your component renders, `useCheckWorkspaceAvailabilityQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useCheckWorkspaceAvailabilityQuery({
 *   variables: {
 *      slug: // value for 'slug'
 *   },
 * });
 */
export function useCheckWorkspaceAvailabilityQuery(baseOptions: Apollo.QueryHookOptions<CheckWorkspaceAvailabilityQuery, CheckWorkspaceAvailabilityQueryVariables> & ({ variables: CheckWorkspaceAvailabilityQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<CheckWorkspaceAvailabilityQuery, CheckWorkspaceAvailabilityQueryVariables>(CheckWorkspaceAvailabilityDocument, options);
      }
export function useCheckWorkspaceAvailabilityLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<CheckWorkspaceAvailabilityQuery, CheckWorkspaceAvailabilityQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<CheckWorkspaceAvailabilityQuery, CheckWorkspaceAvailabilityQueryVariables>(CheckWorkspaceAvailabilityDocument, options);
        }
export function useCheckWorkspaceAvailabilitySuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<CheckWorkspaceAvailabilityQuery, CheckWorkspaceAvailabilityQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<CheckWorkspaceAvailabilityQuery, CheckWorkspaceAvailabilityQueryVariables>(CheckWorkspaceAvailabilityDocument, options);
        }
export type CheckWorkspaceAvailabilityQueryHookResult = ReturnType<typeof useCheckWorkspaceAvailabilityQuery>;
export type CheckWorkspaceAvailabilityLazyQueryHookResult = ReturnType<typeof useCheckWorkspaceAvailabilityLazyQuery>;
export type CheckWorkspaceAvailabilitySuspenseQueryHookResult = ReturnType<typeof useCheckWorkspaceAvailabilitySuspenseQuery>;
export type CheckWorkspaceAvailabilityQueryResult = Apollo.QueryResult<CheckWorkspaceAvailabilityQuery, CheckWorkspaceAvailabilityQueryVariables>;
export const WorkspaceTemplatesPageDocument = gql`
    query WorkspaceTemplatesPage($workspaceSlug: String!, $page: Int, $perPage: Int) {
  workspace(slug: $workspaceSlug) {
    slug
    name
    ...WorkspaceLayout_workspace
  }
  pipelineTemplates(workspaceSlug: $workspaceSlug, page: $page, perPage: $perPage) {
    items {
      ...TemplateCard_template
    }
    totalItems
    totalPages
    pageNumber
  }
}
    ${WorkspaceLayout_WorkspaceFragmentDoc}
${TemplateCard_TemplateFragmentDoc}`;

/**
 * __useWorkspaceTemplatesPageQuery__
 *
 * To run a query within a React component, call `useWorkspaceTemplatesPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspaceTemplatesPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspaceTemplatesPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useWorkspaceTemplatesPageQuery(baseOptions: Apollo.QueryHookOptions<WorkspaceTemplatesPageQuery, WorkspaceTemplatesPageQueryVariables> & ({ variables: WorkspaceTemplatesPageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspaceTemplatesPageQuery, WorkspaceTemplatesPageQueryVariables>(WorkspaceTemplatesPageDocument, options);
      }
export function useWorkspaceTemplatesPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspaceTemplatesPageQuery, WorkspaceTemplatesPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspaceTemplatesPageQuery, WorkspaceTemplatesPageQueryVariables>(WorkspaceTemplatesPageDocument, options);
        }
export function useWorkspaceTemplatesPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspaceTemplatesPageQuery, WorkspaceTemplatesPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspaceTemplatesPageQuery, WorkspaceTemplatesPageQueryVariables>(WorkspaceTemplatesPageDocument, options);
        }
export type WorkspaceTemplatesPageQueryHookResult = ReturnType<typeof useWorkspaceTemplatesPageQuery>;
export type WorkspaceTemplatesPageLazyQueryHookResult = ReturnType<typeof useWorkspaceTemplatesPageLazyQuery>;
export type WorkspaceTemplatesPageSuspenseQueryHookResult = ReturnType<typeof useWorkspaceTemplatesPageSuspenseQuery>;
export type WorkspaceTemplatesPageQueryResult = Apollo.QueryResult<WorkspaceTemplatesPageQuery, WorkspaceTemplatesPageQueryVariables>;
export const WorkspaceTemplatePageDocument = gql`
    query WorkspaceTemplatePage($workspaceSlug: String!, $templateCode: String!) {
  workspace(slug: $workspaceSlug) {
    slug
    name
    ...PipelineLayout_workspace
  }
  template: templateByCode(code: $templateCode) {
    ...TemplateLayout_template
    permissions {
      update
      delete
    }
    id
    code
    name
    description
    currentVersion {
      id
      versionNumber
    }
  }
}
    ${PipelineLayout_WorkspaceFragmentDoc}
${TemplateLayout_TemplateFragmentDoc}`;

/**
 * __useWorkspaceTemplatePageQuery__
 *
 * To run a query within a React component, call `useWorkspaceTemplatePageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspaceTemplatePageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspaceTemplatePageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      templateCode: // value for 'templateCode'
 *   },
 * });
 */
export function useWorkspaceTemplatePageQuery(baseOptions: Apollo.QueryHookOptions<WorkspaceTemplatePageQuery, WorkspaceTemplatePageQueryVariables> & ({ variables: WorkspaceTemplatePageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspaceTemplatePageQuery, WorkspaceTemplatePageQueryVariables>(WorkspaceTemplatePageDocument, options);
      }
export function useWorkspaceTemplatePageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspaceTemplatePageQuery, WorkspaceTemplatePageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspaceTemplatePageQuery, WorkspaceTemplatePageQueryVariables>(WorkspaceTemplatePageDocument, options);
        }
export function useWorkspaceTemplatePageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspaceTemplatePageQuery, WorkspaceTemplatePageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspaceTemplatePageQuery, WorkspaceTemplatePageQueryVariables>(WorkspaceTemplatePageDocument, options);
        }
export type WorkspaceTemplatePageQueryHookResult = ReturnType<typeof useWorkspaceTemplatePageQuery>;
export type WorkspaceTemplatePageLazyQueryHookResult = ReturnType<typeof useWorkspaceTemplatePageLazyQuery>;
export type WorkspaceTemplatePageSuspenseQueryHookResult = ReturnType<typeof useWorkspaceTemplatePageSuspenseQuery>;
export type WorkspaceTemplatePageQueryResult = Apollo.QueryResult<WorkspaceTemplatePageQuery, WorkspaceTemplatePageQueryVariables>;
export const WorkspaceTemplateVersionsPageDocument = gql`
    query WorkspaceTemplateVersionsPage($workspaceSlug: String!, $templateCode: String!, $page: Int!, $perPage: Int!) {
  workspace(slug: $workspaceSlug) {
    slug
    name
    ...WorkspaceLayout_workspace
  }
  template: templateByCode(code: $templateCode) {
    id
    code
    name
    currentVersion {
      id
    }
    versions(page: $page, perPage: $perPage) {
      items {
        ...TemplateVersionCard_version
        id
      }
      totalItems
      totalPages
    }
  }
}
    ${WorkspaceLayout_WorkspaceFragmentDoc}
${TemplateVersionCard_VersionFragmentDoc}`;

/**
 * __useWorkspaceTemplateVersionsPageQuery__
 *
 * To run a query within a React component, call `useWorkspaceTemplateVersionsPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspaceTemplateVersionsPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspaceTemplateVersionsPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      templateCode: // value for 'templateCode'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useWorkspaceTemplateVersionsPageQuery(baseOptions: Apollo.QueryHookOptions<WorkspaceTemplateVersionsPageQuery, WorkspaceTemplateVersionsPageQueryVariables> & ({ variables: WorkspaceTemplateVersionsPageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspaceTemplateVersionsPageQuery, WorkspaceTemplateVersionsPageQueryVariables>(WorkspaceTemplateVersionsPageDocument, options);
      }
export function useWorkspaceTemplateVersionsPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspaceTemplateVersionsPageQuery, WorkspaceTemplateVersionsPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspaceTemplateVersionsPageQuery, WorkspaceTemplateVersionsPageQueryVariables>(WorkspaceTemplateVersionsPageDocument, options);
        }
export function useWorkspaceTemplateVersionsPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspaceTemplateVersionsPageQuery, WorkspaceTemplateVersionsPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspaceTemplateVersionsPageQuery, WorkspaceTemplateVersionsPageQueryVariables>(WorkspaceTemplateVersionsPageDocument, options);
        }
export type WorkspaceTemplateVersionsPageQueryHookResult = ReturnType<typeof useWorkspaceTemplateVersionsPageQuery>;
export type WorkspaceTemplateVersionsPageLazyQueryHookResult = ReturnType<typeof useWorkspaceTemplateVersionsPageLazyQuery>;
export type WorkspaceTemplateVersionsPageSuspenseQueryHookResult = ReturnType<typeof useWorkspaceTemplateVersionsPageSuspenseQuery>;
export type WorkspaceTemplateVersionsPageQueryResult = Apollo.QueryResult<WorkspaceTemplateVersionsPageQuery, WorkspaceTemplateVersionsPageQueryVariables>;