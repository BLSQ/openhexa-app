import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { CountryPicker_CountryFragmentDoc } from '../../../core/features/CountryPicker/CountryPicker.generated';
export type DuplicateWorkspaceDialog_RunFragment = { __typename?: 'WorkspaceCopyRun', id: string, status: Types.WorkspaceCopyRunStatus, targetWorkspaceName: string, sourceWorkspaceSlug: string, error?: string | null, warnings: Array<string>, sourceWorkspace?: { __typename?: 'Workspace', slug: string, name: string } | null, steps: Array<{ __typename?: 'WorkspaceCopyStep', name: Types.WorkspaceCopyStepName, status: Types.WorkspaceCopyStepStatus }>, workspace?: { __typename?: 'Workspace', slug: string, name: string } | null };

export type DuplicateWorkspace_WorkspaceFragment = { __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', code: string, alpha3: string, name: string }>, permissions: { __typename?: 'WorkspacePermissions', duplicate: boolean } };

export const DuplicateWorkspaceDialog_RunFragmentDoc = gql`
    fragment DuplicateWorkspaceDialog_run on WorkspaceCopyRun {
  id
  status
  targetWorkspaceName
  sourceWorkspaceSlug
  sourceWorkspace {
    slug
    name
  }
  error
  steps {
    name
    status
  }
  warnings
  workspace {
    slug
    name
  }
}
    `;
export const DuplicateWorkspace_WorkspaceFragmentDoc = gql`
    fragment DuplicateWorkspace_workspace on Workspace {
  slug
  name
  countries {
    ...CountryPicker_country
  }
  permissions {
    duplicate
  }
}
    ${CountryPicker_CountryFragmentDoc}`;