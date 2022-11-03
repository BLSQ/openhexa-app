import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
import { CollectionDeleteTrigger_CollectionFragmentDoc } from './CollectionDeleteTrigger.generated';
export type CollectionActionsMenu_CollectionFragment = { __typename?: 'Collection', id: string, name: string, permissions: { __typename?: 'CollectionPermissions', delete: boolean } };

export const CollectionActionsMenu_CollectionFragmentDoc = gql`
    fragment CollectionActionsMenu_collection on Collection {
  id
  permissions {
    delete
  }
  ...CollectionDeleteTrigger_collection
}
    ${CollectionDeleteTrigger_CollectionFragmentDoc}`;