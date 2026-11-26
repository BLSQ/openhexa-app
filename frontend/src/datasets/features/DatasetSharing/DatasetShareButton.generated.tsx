import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type DatasetShareButton_DatasetFragment = { __typename?: 'Dataset', id: string, slug: string, publicSlug?: string | null, visibility: Types.DatasetVisibility, permissions: { __typename?: 'DatasetPermissions', update: boolean, share: boolean } };

export const DatasetShareButton_DatasetFragmentDoc = gql`
    fragment DatasetShareButton_dataset on Dataset {
  id
  slug
  publicSlug
  visibility
  permissions {
    update
    share
  }
}
    `;