import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
export type CollectionElementDeleteTrigger_CollectionFragment = { __typename?: 'Collection', id: string, permissions: { __typename?: 'CollectionPermissions', update: boolean } };

export type CollectionElementDeleteTrigger_ElementFragment = { __typename?: 'CollectionElement', id: string, name: string };

export const CollectionElementDeleteTrigger_CollectionFragmentDoc = gql`
    fragment CollectionElementDeleteTrigger_collection on Collection {
  id
  permissions {
    update
  }
}
    `;
export const CollectionElementDeleteTrigger_ElementFragmentDoc = gql`
    fragment CollectionElementDeleteTrigger_element on CollectionElement {
  id
  name
}
    `;