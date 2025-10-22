import { graphql } from "graphql/gql";

export const FavoriteWebappButtonWebappDoc = graphql(`
fragment FavoriteWebappButton_webapp on Webapp {
  id
  isFavorite
}
`);
