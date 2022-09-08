import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
import { CountryBadge_CountryFragmentDoc } from '../../core/features/CountryBadge.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type ManageCollectionItemDialogQueryVariables = Types.Exact<{ [key: string]: never; }>;


export type ManageCollectionItemDialogQuery = { __typename?: 'Query', collections: { __typename?: 'CollectionPage', items: Array<{ __typename?: 'Collection', id: string, name: string, summary?: string | null, elements: { __typename?: 'CollectionElementPage', items: Array<{ __typename?: 'CollectionElement', id: string, objectId: string, app: string, model: string }> }, countries: Array<{ __typename?: 'Country', code: string, name: string, flag: string }> }> } };


export const ManageCollectionItemDialogDocument = gql`
    query ManageCollectionItemDialog {
  collections {
    items {
      id
      name
      summary
      elements {
        items {
          id
          objectId
          app
          model
        }
      }
      countries {
        ...CountryBadge_country
      }
    }
  }
}
    ${CountryBadge_CountryFragmentDoc}`;

/**
 * __useManageCollectionItemDialogQuery__
 *
 * To run a query within a React component, call `useManageCollectionItemDialogQuery` and pass it any options that fit your needs.
 * When your component renders, `useManageCollectionItemDialogQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useManageCollectionItemDialogQuery({
 *   variables: {
 *   },
 * });
 */
export function useManageCollectionItemDialogQuery(baseOptions?: Apollo.QueryHookOptions<ManageCollectionItemDialogQuery, ManageCollectionItemDialogQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<ManageCollectionItemDialogQuery, ManageCollectionItemDialogQueryVariables>(ManageCollectionItemDialogDocument, options);
      }
export function useManageCollectionItemDialogLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<ManageCollectionItemDialogQuery, ManageCollectionItemDialogQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<ManageCollectionItemDialogQuery, ManageCollectionItemDialogQueryVariables>(ManageCollectionItemDialogDocument, options);
        }
export type ManageCollectionItemDialogQueryHookResult = ReturnType<typeof useManageCollectionItemDialogQuery>;
export type ManageCollectionItemDialogLazyQueryHookResult = ReturnType<typeof useManageCollectionItemDialogLazyQuery>;
export type ManageCollectionItemDialogQueryResult = Apollo.QueryResult<ManageCollectionItemDialogQuery, ManageCollectionItemDialogQueryVariables>;