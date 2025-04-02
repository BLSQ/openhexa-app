import { gql } from "@apollo/client";
import { getApolloClient } from "core/helpers/apollo";
import { RunDagError } from "graphql/types";
import {
  GetPipelineVersionQuery,
  GetPipelineVersionQueryVariables,
  RunPipelineMutation,
} from "./pipeline.generated";

export async function runPipeline(pipelineId: string, config: object = {}) {
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

export async function downloadPipelineVersion(versionId: string) {
  const client = getApolloClient();
  const { data } = await client.query<
    GetPipelineVersionQuery,
    GetPipelineVersionQueryVariables
  >({
    query: gql`
      query GetPipelineVersion($versionId: UUID!) {
        pipelineVersion(id: $versionId) {
          id
          versionName
          pipeline {
            code
          }
          zipfile
        }
      }
    `,
    variables: { versionId },
  });
  if (!data.pipelineVersion) {
    throw new Error(`No version found for ${versionId}`);
  }
  const { zipfile, pipeline } = data.pipelineVersion;
  const blob = new Blob([Buffer.from(zipfile, "base64")], {
    type: "application/zip",
  });
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `${pipeline.code}-${encodeURIComponent(
    data.pipelineVersion.versionName,
  )}.zip`;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  window.URL.revokeObjectURL(url);
}
