import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type WorkspacePicker_ValueFragment = { __typename?: 'Workspace', slug: string, name: string };

export const WorkspacePicker_ValueFragmentDoc = gql`
    fragment WorkspacePicker_value on Workspace {
  slug
  name
}
    `;