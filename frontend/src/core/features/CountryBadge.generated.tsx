import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
export type CountryBadge_CountryFragment = { __typename?: 'Country', code: string, name: string };

export const CountryBadge_CountryFragmentDoc = gql`
    fragment CountryBadge_country on Country {
  code
  name
}
    `;