import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
export type CollectionDeleteTrigger_CollectionFragment = { __typename?: 'Collection', id: string, name: string, authorizedActions: { __typename?: 'CollectionAuthorizedActions', canDelete: boolean } };

export const CollectionDeleteTrigger_CollectionFragmentDoc = gql`
    fragment CollectionDeleteTrigger_collection on Collection {
  id
  name
  authorizedActions {
    canDelete
  }
}
    `;