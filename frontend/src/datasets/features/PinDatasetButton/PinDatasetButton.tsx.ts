import { graphql } from "graphql/gql";

export const PinDatasetButtonLinkDoc = graphql(`
fragment PinDatasetButton_link on DatasetLink {
  id
  isPinned
  permissions {
    pin
  }
}
`);
