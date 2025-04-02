import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type FavoriteWebappButton_WebappFragment = { __typename?: 'Webapp', id: string, isFavorite: boolean };

export const FavoriteWebappButton_WebappFragmentDoc = gql`
    fragment FavoriteWebappButton_webapp on Webapp {
  id
  isFavorite
}
    `;