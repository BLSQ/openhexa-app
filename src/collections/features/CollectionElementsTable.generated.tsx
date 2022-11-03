import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
import { CollectionElementDeleteTrigger_CollectionFragmentDoc } from './CollectionElementDeleteTrigger.generated';
import { CollectionElementDeleteTrigger_ElementFragmentDoc } from './CollectionElementDeleteTrigger.generated';
export type CollectionElementsTable_CollectionFragment = { __typename?: 'Collection', id: string, permissions: { __typename?: 'CollectionPermissions', update: boolean } };

export type CollectionElementsTable_ElementFragment = { __typename?: 'CollectionElement', id: string, createdAt: any, updatedAt: any, name: string, type: string, app: string, model: string, url?: any | null, objectId: string };

export const CollectionElementsTable_CollectionFragmentDoc = gql`
    fragment CollectionElementsTable_collection on Collection {
  id
  ...CollectionElementDeleteTrigger_collection
}
    ${CollectionElementDeleteTrigger_CollectionFragmentDoc}`;
export const CollectionElementsTable_ElementFragmentDoc = gql`
    fragment CollectionElementsTable_element on CollectionElement {
  ...CollectionElementDeleteTrigger_element
  id
  createdAt
  updatedAt
  name
  type
  app
  model
  url
  objectId
}
    ${CollectionElementDeleteTrigger_ElementFragmentDoc}`;