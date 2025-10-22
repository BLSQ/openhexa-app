import { graphql } from "graphql/gql";

export const TagTagDoc = graphql(`
fragment Tag_tag on Tag {
  id
  name
}
`);
