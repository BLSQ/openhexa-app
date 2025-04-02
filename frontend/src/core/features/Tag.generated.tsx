import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
export type Tag_TagFragment = { __typename?: 'Tag', id: string, name: string };

export const Tag_TagFragmentDoc = gql`
    fragment Tag_tag on Tag {
  id
  name
}
    `;