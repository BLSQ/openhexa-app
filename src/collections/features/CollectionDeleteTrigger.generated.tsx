import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
export type CollectionDeleteTrigger_CollectionFragment = { __typename?: 'Collection', id: string, name: string, permissions: { __typename?: 'CollectionPermissions', delete: boolean } };

export const CollectionDeleteTrigger_CollectionFragmentDoc = gql`
    fragment CollectionDeleteTrigger_collection on Collection {
  id
  name
  permissions {
    delete
  }
}
    `;