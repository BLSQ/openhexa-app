import { gql } from "@apollo/client";
import { getApolloClient } from "core/helpers/apollo";
import cronstrue from "cronstrue";
import CronParser from "cron-parser";
import "cronstrue/locales/en";
import "cronstrue/locales/fr";
import {
  ConnectionType,
  PipelineNotificationLevel,
  PipelineParameter,
  PipelineType,
  UpdatePipelineError,
} from "graphql/types";
import { i18n } from "next-i18next";
import {
  RunWorkspacePipelineMutation,
  UpdateWorkspacePipelineMutation,
  UpdateWorkspacePipelineMutationVariables,
} from "./pipelines.generated";

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
  } else if (
    data?.updatePipeline.errors.includes(UpdatePipelineError.PermissionDenied)
  ) {
    throw new Error("You are not authorized to perform this action");
  } else if (
    data?.updatePipeline.errors.includes(
      UpdatePipelineError.MissingVersionConfig,
    )
  ) {
    throw new Error(
      "This pipeline has required parameters that have not been set. Edit the default parameters to fix this issue.",
    );
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
  version: { parameters: { code: string; type: string; multiple: boolean }[] },
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
      } else if (val !== undefined && val !== null && val !== "") {
        params[parameter.code] = parseInt(val, 10);
      }
    } else if (parameter.type === "float") {
      if (parameter.multiple && val) {
        params[parameter.code] = val
          .filter((v: string) => v !== "")
          .map((v: string) => parseFloat(v));
      } else if (val !== undefined && val !== null && val !== "") {
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
  config: any = {},
  versionId?: string,
  sendMailNotifications?: boolean,
  enableDebugLogs?: boolean,
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
      input: {
        id: pipelineId,
        config,
        versionId,
        sendMailNotifications,
        enableDebugLogs,
      },
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
  version?: { parameters: Omit<PipelineParameter, "__typename">[] } | null;
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

export function toSpinalCase(str: string) {
  return str
    .replace(/(?!^)([A-Z])/g, " $1")
    .replace(/[^A-Za-z0-9]/g, "-")
    .toLowerCase();
}

export async function deletePipelineVersion(versionId: string) {
  const client = getApolloClient();
  const { data } = await client.mutate({
    mutation: gql`
      mutation DeletePipelineVersion($input: DeletePipelineVersionInput!) {
        deletePipelineVersion(input: $input) {
          success
          errors
        }
      }
    `,
    variables: { input: { id: versionId } },
  });

  if (data.deletePipelineVersion.success) {
    return true;
  }

  if (data.deletePipelineVersion.errors.includes("PERMISSION_DENIED")) {
    throw new Error("You are not authorized to perform this action");
  }

  throw new Error("Failed to delete pipeline version");
}

export function formatPipelineType(pipelineType: PipelineType) {
  switch (pipelineType) {
    case PipelineType.Notebook:
      return i18n!.t("Jupyter notebook");
    case PipelineType.ZipFile:
      return i18n!.t("Standard pipeline");
    default:
      return i18n!.t("Pipeline");
  }
}

export async function createPipelineRecipient(
  pipelineId: string,
  userId: string,
  notificationLevel: string,
) {
  const client = getApolloClient();

  const { data } = await client.mutate({
    mutation: gql`
      mutation addPipelineRecipient($input: CreatePipelineRecipientInput!) {
        addPipelineRecipient(input: $input) {
          success
          errors
        }
      }
    `,
    variables: { input: { userId, pipelineId, notificationLevel } },
  });

  if (data.addPipelineRecipient.success) {
    return true;
  }

  if (data.addPipelineRecipient.errors.includes("PERMISSION_DENIED")) {
    throw new Error("You are not authorized to perform this action");
  }

  throw new Error("Failed to create recipient.");
}

export async function updatePipelineRecipient(
  recipientId: string,
  notificationLevel: PipelineNotificationLevel,
) {
  const client = getApolloClient();

  const { data } = await client.mutate({
    mutation: gql`
      mutation updatePipelineRecipient($input: UpdatePipelineRecipientInput!) {
        updatePipelineRecipient(input: $input) {
          success
          errors
          recipient {
            id
            notificationLevel
          }
        }
      }
    `,
    variables: { input: { recipientId, notificationLevel } },
  });

  if (data.updatePipelineRecipient.success) {
    return true;
  }

  if (data.updatePipelineRecipient.errors.includes("PERMISSION_DENIED")) {
    throw new Error("You are not authorized to perform this action");
  }

  throw new Error("Failed to update recipient");
}

export async function deletePipelineRecipient(recipientId: string) {
  const client = getApolloClient();
  const { data } = await client.mutate({
    mutation: gql`
      mutation deletePipelineRecipient($input: DeletePipelineRecipientInput!) {
        deletePipelineRecipient(input: $input) {
          success
          errors
        }
      }
    `,
    variables: { input: { recipientId } },
  });

  if (data.deletePipelineRecipient.success) {
    return true;
  }

  if (data.deletePipelineRecipient.errors.includes("PERMISSION_DENIED")) {
    throw new Error("You are not authorized to perform this action");
  }

  throw new Error("Failed to delete recipient");
}
