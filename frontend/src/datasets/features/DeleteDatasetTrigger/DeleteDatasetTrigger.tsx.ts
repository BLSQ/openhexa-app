import { graphql } from "graphql/gql";

export const DeleteDatasetTriggerDatasetDoc = graphql(`
fragment DeleteDatasetTrigger_dataset on Dataset {
  id
  name
  workspace {
    slug
  }
  permissions {
    delete
  }
}
`);
