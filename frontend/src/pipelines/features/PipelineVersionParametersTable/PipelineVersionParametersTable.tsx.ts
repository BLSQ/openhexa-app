import { graphql } from "graphql/gql";

export const PipelineVersionParametersTableVersionDoc = graphql(`
fragment PipelineVersionParametersTable_version on PipelineVersion {
  id
  parameters {
    ...ParameterField_parameter
  }
  config
}
`);
