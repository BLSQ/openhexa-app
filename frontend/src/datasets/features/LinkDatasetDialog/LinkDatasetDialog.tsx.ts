import { graphql } from "graphql/gql";

export const LinkDatasetDialogDatasetDoc = graphql(`
fragment LinkDatasetDialog_dataset on Dataset {
  id
  name
}
`);
