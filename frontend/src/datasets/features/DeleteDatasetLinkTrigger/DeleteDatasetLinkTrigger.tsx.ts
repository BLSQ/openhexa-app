import { graphql } from "graphql/gql";

export const DeleteDatasetLinkTriggerDatasetLinkDoc = graphql(`
fragment DeleteDatasetLinkTrigger_datasetLink on DatasetLink {
  id
  dataset {
    name
    id
  }
  workspace {
    slug
  }
  permissions {
    delete
  }
}
`);
