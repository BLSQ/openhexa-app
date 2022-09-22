import { gql } from "@apollo/client";
import { getApolloClient } from "core/helpers/apollo";
import { IncomingMessage } from "http";
import {
  GetPipelineRunQuery,
  GetRunOutputDownloadUrlMutation,
} from "./runs.generated";

export async function getPipelineRun(runId: string, req: IncomingMessage) {
  const client = getApolloClient(req);

  try {
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
    return data.dagRun;
  } catch {
    throw new Error(`Run ${runId} not found`);
  }
}

export async function getRunOutputDownloadURL(uri: string) {
  const client = getApolloClient();

  const { data } = await client.mutate<GetRunOutputDownloadUrlMutation>({
    mutation: gql`
      mutation GetRunOutputDownloadURL($input: PrepareDownloadURLInput!) {
        prepareDownloadURL(input: $input) {
          success
          url
        }
      }
    `,
    variables: { input: { uri } },
  });

  return data?.prepareDownloadURL?.url;
}
