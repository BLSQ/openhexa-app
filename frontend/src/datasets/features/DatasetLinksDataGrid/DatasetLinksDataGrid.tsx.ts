import { graphql } from "graphql/gql";

export const DatasetLinksDataGridDatasetDoc = graphql(`
fragment DatasetLinksDataGrid_dataset on Dataset {
  id
  name
}
`);
