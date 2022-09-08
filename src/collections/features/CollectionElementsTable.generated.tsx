import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
export type CollectionElementsTable_ElementFragment = { __typename?: 'CollectionElement', id: string, createdAt: any, updatedAt: any, name: string, type: string, app: string, model: string, url?: any | null, objectId: string };

export const CollectionElementsTable_ElementFragmentDoc = gql`
    fragment CollectionElementsTable_element on CollectionElement {
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
    `;