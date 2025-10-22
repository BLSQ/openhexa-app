import { graphql } from "graphql/gql";

export const CountryPickerCountryDoc = graphql(`
fragment CountryPicker_country on Country {
  code
  alpha3
  name
}
`);
