import { gql } from "@apollo/client";
import { getApolloClient } from "core/helpers/apollo";
import {
  RunWorkspacePipelineMutation,
  UpdateWorkspacePipelineMutation,
  UpdateWorkspacePipelineMutationVariables,
} from "./pipelines.generated";
import cronstrue from "cronstrue/i18n";
import "cronstrue/locales/fr";
import CronParser from "cron-parser";
import { PipelineRun } from "graphql-types";

export type Parameter = {
  help: string;
  name: string;
  choices?: null | string[];
  required?: boolean;
  type: "str" | "bool" | "int" | "float";
};

export async function updatePipeline(pipelineId: string, values: any) {
  const client = getApolloClient();
  const { data } = await client.mutate<
    UpdateWorkspacePipelineMutation,
    UpdateWorkspacePipelineMutationVariables
  >({
    mutation: gql`
      mutation UpdateWorkspacePipeline($input: UpdatePipelineInput!) {
        updatePipeline(input: $input) {
          success
          errors
          pipeline {
            id
            name
            description
            schedule
            config
            updatedAt
          }
        }
      }
    `,
    variables: { input: { id: pipelineId, ...values } },
  });

  if (data?.updatePipeline.success) {
    return data.updatePipeline.pipeline;
  }

  throw new Error("Failed to update pipeline");
}

export function validateCronExpression(cronExpression: string) {
  try {
    CronParser.parseExpression(cronExpression);
    return true;
  } catch (err) {
    return false;
  }
}

export function getCronExpressionDescription(
  cronExpression: string,
  locale?: "en" | "fr"
) {
  if (!validateCronExpression(cronExpression)) {
    return null;
  }
  try {
    return cronstrue.toString(cronExpression, { locale });
  } catch (err) {
    return null;
  }
}

export async function runPipeline(
  pipelineId: string,
  config: any,
  version?: number
) {
  const client = getApolloClient();
  const { data } = await client.mutate<RunWorkspacePipelineMutation>({
    mutation: gql`
      mutation RunWorkspacePipeline($input: RunPipelineInput!) {
        runPipeline(input: $input) {
          success
          errors
          run {
            id
          }
        }
      }
    `,
    variables: { input: { id: pipelineId, config, version } },
  });

  if (data?.runPipeline.success && data.runPipeline.run) {
    return data.runPipeline.run;
  } else if (
    data?.runPipeline.errors.some((e: any) =>
      ["PIPELINE_NOT_FOUND", "PIPELINE_VERSION_NOT_FOUND"].includes(e)
    )
  ) {
    throw new Error("Pipeline not found");
  } else if (data?.runPipeline.errors.some((e) => e === "INVALID_CONFIG")) {
    throw new Error("Invalid pipeline configuration");
  } else {
    throw new Error("Failed to run pipeline");
  }
}

export function getPipelineRunConfig(run: {
  config: any;
  version: { parameters: any };
}) {
  const config = run.config || {};
  const parameters = run.version?.parameters || [];

  return parameters.map((param: any) => ({
    value: config[param.name],
    ...param,
  })) as (Parameter & { value: any })[];
}
