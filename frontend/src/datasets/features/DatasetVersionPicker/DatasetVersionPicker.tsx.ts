import { graphql } from "graphql/gql";

export const DatasetVersionPickerVersionDoc = graphql(`
fragment DatasetVersionPicker_version on DatasetVersion {
  id
  name
  createdAt
}
`);

export const DatasetVersionPickerDatasetDoc = graphql(`
fragment DatasetVersionPicker_dataset on Dataset {
  id
}
`);
