import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type ShortcutWebappButton_WebappFragment = { __typename?: 'Webapp', id: string, isShortcut: boolean };

export const ShortcutWebappButton_WebappFragmentDoc = gql`
    fragment ShortcutWebappButton_webapp on Webapp {
  id
  isShortcut
}
    `;