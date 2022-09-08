import * as Types from '../../../graphql-types';

import { gql } from '@apollo/client';
export type Quicksearch_CollectionFragment = { __typename?: 'Collection', id: string };

export const Quicksearch_CollectionFragmentDoc = gql`
    fragment Quicksearch_collection on Collection {
  id
}
    `;