import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
import { CollectionDeleteTrigger_CollectionFragmentDoc } from './CollectionDeleteTrigger.generated';
export type CollectionActionsMenu_CollectionFragment = { __typename?: 'Collection', id: string, name: string, authorizedActions: { __typename?: 'CollectionAuthorizedActions', canDelete: boolean, canUpdate: boolean } };

export const CollectionActionsMenu_CollectionFragmentDoc = gql`
    fragment CollectionActionsMenu_collection on Collection {
  id
  authorizedActions {
    canDelete
    canUpdate
  }
  ...CollectionDeleteTrigger_collection
}
    ${CollectionDeleteTrigger_CollectionFragmentDoc}`;