import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
export type CollectionElementsTable_Element_Dhis2DataElementCollectionElement_Fragment = { __typename?: 'DHIS2DataElementCollectionElement', id: string, createdAt: any, updatedAt: any, dhis2: { __typename?: 'DHIS2DataElement', id: string, name: string, code: string, instance: { __typename?: 'DHIS2Instance', id: string, name: string } } };

export type CollectionElementsTable_Element_S3ObjectCollectionElement_Fragment = { __typename?: 'S3ObjectCollectionElement', id: string, createdAt: any, updatedAt: any, s3: { __typename?: 'S3Object', id: string, type: string, size: number, key: string, filename: string, storageClass: string, bucket: { __typename?: 'S3Bucket', id: string, name: string } } };

export type CollectionElementsTable_ElementFragment = CollectionElementsTable_Element_Dhis2DataElementCollectionElement_Fragment | CollectionElementsTable_Element_S3ObjectCollectionElement_Fragment;

export const CollectionElementsTable_ElementFragmentDoc = gql`
    fragment CollectionElementsTable_element on CollectionElement {
  id
  createdAt
  updatedAt
  ... on DHIS2DataElementCollectionElement {
    dhis2: element {
      id
      name
      code
      instance {
        id
        name
      }
    }
  }
  ... on S3ObjectCollectionElement {
    s3: element {
      id
      type
      size
      key
      filename
      storageClass
      bucket {
        id
        name
      }
    }
  }
}
    `;