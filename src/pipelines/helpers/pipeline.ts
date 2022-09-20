import { gql } from "@apollo/client";
import { getApolloClient } from "core/helpers/apollo";
import { RunDagError } from "graphql-types";
import { RunPipelineMutation } from "./pipeline.generated";

export async function runPipeline(pipelineId: string, config: object) {
  const client = getApolloClient();
  const { data } = await client.mutate<RunPipelineMutation>({
    mutation: gql`
      mutation RunPipeline($input: RunDAGInput!) {
        runDAG(input: $input) {
          success
          errors
          dag {
            id
          }
          dagRun {
            id
            externalUrl
            externalId
          }
        }
      }
    `,
    variables: { input: { dagId: pipelineId, config } },
  });

  if (!data?.runDAG.success) {
    if (data?.runDAG.errors.includes(RunDagError.DagNotFound)) {
      throw new Error("DAG not found");
    } else if (data?.runDAG.errors.includes(RunDagError.InvalidConfig)) {
      throw new Error("Invalid configuration");
    } else {
      throw new Error("Unknown error");
    }
  }
  return { dag: data.runDAG.dag!, dagRun: data.runDAG.dagRun! };
}
