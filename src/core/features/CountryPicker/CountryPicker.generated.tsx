import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type CountryPickerQueryVariables = Types.Exact<{ [key: string]: never; }>;


export type CountryPickerQuery = { __typename?: 'Query', countries: Array<{ __typename?: 'Country', code: string, alpha3: string, name: string }> };

export type CountryPicker_CountryFragment = { __typename?: 'Country', code: string, alpha3: string, name: string };

export const CountryPicker_CountryFragmentDoc = gql`
    fragment CountryPicker_country on Country {
  code
  alpha3
  name
}
    `;
export const CountryPickerDocument = gql`
    query CountryPicker {
  countries {
    ...CountryPicker_country
  }
}
    ${CountryPicker_CountryFragmentDoc}`;

/**
 * __useCountryPickerQuery__
 *
 * To run a query within a React component, call `useCountryPickerQuery` and pass it any options that fit your needs.
 * When your component renders, `useCountryPickerQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useCountryPickerQuery({
 *   variables: {
 *   },
 * });
 */
export function useCountryPickerQuery(baseOptions?: Apollo.QueryHookOptions<CountryPickerQuery, CountryPickerQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<CountryPickerQuery, CountryPickerQueryVariables>(CountryPickerDocument, options);
      }
export function useCountryPickerLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<CountryPickerQuery, CountryPickerQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<CountryPickerQuery, CountryPickerQueryVariables>(CountryPickerDocument, options);
        }
export function useCountryPickerSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<CountryPickerQuery, CountryPickerQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<CountryPickerQuery, CountryPickerQueryVariables>(CountryPickerDocument, options);
        }
export type CountryPickerQueryHookResult = ReturnType<typeof useCountryPickerQuery>;
export type CountryPickerLazyQueryHookResult = ReturnType<typeof useCountryPickerLazyQuery>;
export type CountryPickerSuspenseQueryHookResult = ReturnType<typeof useCountryPickerSuspenseQuery>;
export type CountryPickerQueryResult = Apollo.QueryResult<CountryPickerQuery, CountryPickerQueryVariables>;