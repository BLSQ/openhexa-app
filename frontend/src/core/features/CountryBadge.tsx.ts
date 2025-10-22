import { graphql } from "graphql/gql";

export const CountryBadgeCountryDoc = graphql(`
fragment CountryBadge_country on Country {
  code
  name
}
`);
