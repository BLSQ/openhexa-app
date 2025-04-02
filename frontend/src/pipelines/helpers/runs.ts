import { gql } from "@apollo/client";
import { getApolloClient } from "core/helpers/apollo";
import { DagRunTrigger } from "graphql/types";
import { IncomingMessage } from "http";
import { i18n } from "next-i18next";
import {
  GetPipelineRunQuery,
  GetRunOutputDownloadUrlMutation,
} from "./runs.generated";

export async function getPipelineRun(runId: string, req: IncomingMessage) {
  const client = getApolloClient(req);

  try {
    const { data } = await client.query<GetPipelineRunQuery>({
      query: gql`
        query GetPipelineRun($runId: UUID!) {
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

export function getPipelineRunLabel(
  run: {
    label?: string | null;
    externalId?: string | null;
    triggerMode?: DagRunTrigger | null;
    user?: {
      displayName: string;
    } | null;
  },
  pipeline: { label: string | null; externalId: string },
) {
  if (run.label) {
    return run.label;
  } else if (run.triggerMode === DagRunTrigger.Manual) {
    return i18n!.t("Manual run of {{label}} by {{user}}", {
      label: pipeline.label || pipeline.externalId,
      user: run.user?.displayName ?? i18n!.t("a user"),
    });
  } else if (run.triggerMode === DagRunTrigger.Scheduled) {
    return i18n!.t("Scheduled run of {{label}}", {
      label: pipeline.label || pipeline.externalId,
    });
  } else {
    return i18n!.t("Run of {{label}}", {
      label: pipeline.label || pipeline.externalId,
    });
  }
}
