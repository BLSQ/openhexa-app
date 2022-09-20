import { gql } from "@apollo/client";
import { getApolloClient } from "core/helpers/apollo";
import { GetPipelineRunQuery } from "./runs.generated";

export async function getPipelineRun(runId: string) {
  const client = getApolloClient();

  const { data } = await client.query<GetPipelineRunQuery>({
    query: gql`
      query GetPipelineRun($runId: String!) {
        dagRun(id: $runId) {
          config
          externalUrl
          externalId
          status
          executionDate
          duration
        }
      }
    `,
    variables: { runId },
  });

  if (!data.dagRun) {
    throw new Error("Run not found");
  }

  return data.dagRun;
}
