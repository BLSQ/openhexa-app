import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type CountryPicker_CountryFragment = { __typename?: 'Country', code: string, alpha3: string, name: string };

export const CountryPicker_CountryFragmentDoc = gql`
    fragment CountryPicker_country on Country {
  code
  alpha3
  name
}
    `;