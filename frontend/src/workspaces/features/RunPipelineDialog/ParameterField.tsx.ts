import { graphql } from "graphql/gql";

export const ParameterFieldParameterDoc = graphql(`
fragment ParameterField_parameter on PipelineParameter {
  code
  name
  help
  type
  default
  required
  choices
  connection
  widget
  multiple
  directory
}
`);
