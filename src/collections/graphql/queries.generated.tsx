import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
import { Tag_TagFragmentDoc } from '../../core/features/Tag.generated';
import { CountryBadge_CountryFragmentDoc } from '../../core/features/CountryBadge.generated';
import { CollectionElementsTable_ElementFragmentDoc } from '../features/CollectionElementsTable.generated';
import { CollectionActionsMenu_CollectionFragmentDoc } from '../features/CollectionActionsMenu.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type CollectionsPageQueryVariables = Types.Exact<{
  page?: Types.InputMaybe<Types.Scalars['Int']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']>;
}>;


export type CollectionsPageQuery = { __typename?: 'Query', collections: { __typename?: 'CollectionPage', pageNumber: number, totalPages: number, totalItems: number, items: Array<{ __typename?: 'Collection', id: string, name: string, tags: Array<{ __typename?: 'Tag', id: string, name: string }>, countries: Array<{ __typename?: 'Country', code: string, name: string, flag: string }>, author?: { __typename?: 'User', displayName: string } | null }> } };

export type CollectionPageQueryVariables = Types.Exact<{
  id: Types.Scalars['String'];
}>;


export type CollectionPageQuery = { __typename?: 'Query', collection?: { __typename?: 'Collection', id: string, name: string, createdAt: any, updatedAt: any, description?: string | null, author?: { __typename?: 'User', displayName: string } | null, countries: Array<{ __typename?: 'Country', code: string, name: string, flag: string }>, tags: Array<{ __typename?: 'Tag', id: string, name: string }>, elements: { __typename?: 'CollectionElementPage', items: Array<{ __typename?: 'DHIS2DataElementCollectionElement', id: string, createdAt: any, updatedAt: any, dhis2: { __typename?: 'DHIS2DataElement', id: string, name: string, code: string, instance: { __typename?: 'DHIS2Instance', id: string, name: string } } } | { __typename?: 'S3ObjectCollectionElement', id: string, createdAt: any, updatedAt: any, s3: { __typename?: 'S3Object', id: string, type: string, size: number, key: string, filename: string, storageClass: string, bucket: { __typename?: 'S3Bucket', id: string, name: string } } }> }, authorizedActions: { __typename?: 'CollectionAuthorizedActions', canDelete: boolean, canUpdate: boolean } } | null };


export const CollectionsPageDocument = gql`
    query CollectionsPage($page: Int = 1, $perPage: Int = 15) {
  collections(page: $page, perPage: $perPage) {
    pageNumber
    totalPages
    totalItems
    items {
      id
      name
      tags {
        ...Tag_tag
        id
      }
      countries {
        ...CountryBadge_country
        code
      }
      author {
        displayName
      }
    }
  }
}
    ${Tag_TagFragmentDoc}
${CountryBadge_CountryFragmentDoc}`;

/**
 * __useCollectionsPageQuery__
 *
 * To run a query within a React component, call `useCollectionsPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useCollectionsPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useCollectionsPageQuery({
 *   variables: {
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useCollectionsPageQuery(baseOptions?: Apollo.QueryHookOptions<CollectionsPageQuery, CollectionsPageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<CollectionsPageQuery, CollectionsPageQueryVariables>(CollectionsPageDocument, options);
      }
export function useCollectionsPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<CollectionsPageQuery, CollectionsPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<CollectionsPageQuery, CollectionsPageQueryVariables>(CollectionsPageDocument, options);
        }
export type CollectionsPageQueryHookResult = ReturnType<typeof useCollectionsPageQuery>;
export type CollectionsPageLazyQueryHookResult = ReturnType<typeof useCollectionsPageLazyQuery>;
export type CollectionsPageQueryResult = Apollo.QueryResult<CollectionsPageQuery, CollectionsPageQueryVariables>;
export const CollectionPageDocument = gql`
    query CollectionPage($id: String!) {
  collection(id: $id) {
    id
    name
    createdAt
    updatedAt
    description
    author {
      displayName
    }
    countries {
      code
      ...CountryBadge_country
    }
    tags {
      id
      ...Tag_tag
    }
    elements {
      items {
        ...CollectionElementsTable_element
      }
    }
    ...CollectionActionsMenu_collection
  }
}
    ${CountryBadge_CountryFragmentDoc}
${Tag_TagFragmentDoc}
${CollectionElementsTable_ElementFragmentDoc}
${CollectionActionsMenu_CollectionFragmentDoc}`;

/**
 * __useCollectionPageQuery__
 *
 * To run a query within a React component, call `useCollectionPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useCollectionPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useCollectionPageQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useCollectionPageQuery(baseOptions: Apollo.QueryHookOptions<CollectionPageQuery, CollectionPageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<CollectionPageQuery, CollectionPageQueryVariables>(CollectionPageDocument, options);
      }
export function useCollectionPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<CollectionPageQuery, CollectionPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<CollectionPageQuery, CollectionPageQueryVariables>(CollectionPageDocument, options);
        }
export type CollectionPageQueryHookResult = ReturnType<typeof useCollectionPageQuery>;
export type CollectionPageLazyQueryHookResult = ReturnType<typeof useCollectionPageLazyQuery>;
export type CollectionPageQueryResult = Apollo.QueryResult<CollectionPageQuery, CollectionPageQueryVariables>;