import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type WorkspaceDisplayFragmentFragment = { __typename?: 'Workspace', name: string, countries: Array<{ __typename?: 'Country', code: string }> };

export const WorkspaceDisplayFragmentFragmentDoc = gql`
    fragment WorkspaceDisplayFragment on Workspace {
  name
  countries {
    code
  }
}
    `;