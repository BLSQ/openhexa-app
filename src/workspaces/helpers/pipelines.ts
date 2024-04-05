import { gql } from "@apollo/client";
import { getApolloClient } from "core/helpers/apollo";
import CronParser from "cron-parser";
import cronstrue from "cronstrue";
import "cronstrue/locales/en";
import "cronstrue/locales/fr";
import {
  RunWorkspacePipelineMutation,
  UpdateWorkspacePipelineMutation,
  UpdateWorkspacePipelineMutationVariables,
} from "./pipelines.generated";
import {
  ConnectionType,
  PipelineParameter,
  PipelineVersion,
} from "graphql-types";
import { i18n } from "next-i18next";

export async function updatePipeline(
  pipelineId: string,
  values: Omit<UpdateWorkspacePipelineMutationVariables["input"], "id">,
) {
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
            webhookEnabled
            webhookUrl
            recipients {
              user {
                id
                displayName
              }
            }
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

export const isConnectionParameter = (type: string) => {
  return Object.values(ConnectionType)
    .map((c) => c.toLowerCase())
    .includes(type.toLowerCase());
};

export const convertParametersToPipelineInput = (
  version: PipelineVersion,
  fields: { [key: string]: any },
): any => {
  const params: { [key: string]: any } = {};
  for (const parameter of version.parameters) {
    const val = fields[parameter.code];

    if (parameter.type === "int") {
      if (parameter.multiple && val) {
        params[parameter.code] = val
          .filter((v: string) => v !== "")
          .map((v: string) => parseInt(v, 10));
      } else if (val !== null && val !== "") {
        params[parameter.code] = parseInt(val, 10);
      }
    } else if (parameter.type === "float") {
      if (parameter.multiple && val) {
        params[parameter.code] = val
          .filter((v: string) => v !== "")
          .map((v: string) => parseFloat(v));
      } else if (val !== null && val !== "") {
        params[parameter.code] = parseFloat(val);
      }
    } else if (parameter.type === "str" && parameter.multiple && val) {
      params[parameter.code] = val.filter((s: string) => s !== "");
    } else if (isConnectionParameter(parameter.type) && val) {
      params[parameter.code] = val;
    } else {
      params[parameter.code] = val;
    }
  }
  return params;
};

export function getCronExpressionDescription(
  cronExpression: string,
  locale?: "en" | "fr",
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
  versionId?: string,
  sendMailNotifications?: boolean,
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
            pipeline {
              __typename
              id
            }
          }
        }
      }
    `,
    variables: {
      input: { id: pipelineId, config, versionId, sendMailNotifications },
    },
    update: (cache, { data }) => {
      if (!data || !data.runPipeline.run) {
        return;
      }
      const {
        runPipeline: { run },
      } = data;
      cache.modify({
        id: cache.identify(run.pipeline),
        fields: {
          runs(existing) {
            const runRef = cache.writeFragment({
              data: run,
              fragment: gql`
                fragment NewRun on PipelineRun {
                  id
                }
              `,
            });
            return {
              ...existing,
              totalItems: existing.totalItems + 1,
              items: [runRef, ...existing.items],
            };
          },
        },
      });
    },
  });

  if (data?.runPipeline.success && data.runPipeline.run) {
    return data.runPipeline.run;
  } else if (
    data?.runPipeline.errors.some((e: any) =>
      ["PIPELINE_NOT_FOUND", "PIPELINE_VERSION_NOT_FOUND"].includes(e),
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
  version: { parameters: Omit<PipelineParameter, "__typename">[] };
}) {
  const config = run.config || {};
  const parameters = run.version?.parameters || [];

  return parameters.map((param: any) => ({
    value: config[param.code],
    ...param,
  })) as (PipelineParameter & { value: any })[];
}

export function renderOutputType(typename: string | undefined) {
  switch (typename) {
    case "BucketObject":
      return i18n!.t("File");
    case "DatabaseTable":
      return i18n!.t("Database table");
    case "DatasetVersion":
      return i18n!.t("Dataset version");
    default:
      return "-";
  }
}
