import { graphql } from "graphql/gql";

export const ColumnMetadataDrawerFileDoc = graphql(`
fragment ColumnMetadataDrawer_file on DatasetVersionFile {
  id
  targetId
  attributes {
    id
    key
    value
    label
    system
    __typename
  }
  properties
}
`);
