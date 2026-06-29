import type { TFunction } from "i18next";
import { TOOL } from "assistant/helpers/tools";

const PREFIX_VERBS: [string, string][] = [
  ["get_", "Reading"],
  ["read_", "Reading"],
  ["list_", "Listing"],
  ["create_", "Creating"],
  ["update_", "Updating"],
  ["delete_", "Deleting"],
  ["run_", "Running"],
  ["write_", "Writing"],
  ["preview_", "Previewing"],
  ["execute_", "Executing"],
];

export function getToolLabels(t: TFunction): Record<string, string> {
  return {
    [TOOL.LIST_WORKSPACES]:               t("Listing workspaces"),
    [TOOL.GET_WORKSPACE]:                 t("Reading workspace"),
    [TOOL.LIST_FILES]:                    t("Listing files"),
    [TOOL.READ_FILE]:                     t("Reading file"),
    [TOOL.WRITE_FILE]:                    t("Writing file"),
    [TOOL.LIST_DATASETS]:                 t("Listing datasets"),
    [TOOL.GET_DATASET]:                   t("Reading dataset"),
    [TOOL.PREVIEW_DATASET_FILE]:          t("Previewing dataset file"),
    [TOOL.CREATE_DATASET]:                t("Creating dataset"),
    [TOOL.CREATE_DATASET_VERSION]:        t("Creating dataset version"),
    [TOOL.LIST_PIPELINES]:                t("Listing pipelines"),
    [TOOL.GET_PIPELINE]:                  t("Reading pipeline"),
    [TOOL.GET_PIPELINE_RUN]:              t("Reading pipeline run"),
    [TOOL.RUN_PIPELINE]:                  t("Running pipeline"),
    [TOOL.UPDATE_PIPELINE]:               t("Updating pipeline"),
    [TOOL.CREATE_PIPELINE]:               t("Creating pipeline"),
    [TOOL.CREATE_PIPELINE_VERSION]:       t("Creating pipeline version"),
    [TOOL.LIST_CONNECTIONS]:              t("Listing connections"),
    [TOOL.LIST_PIPELINE_TEMPLATES]:       t("Listing pipeline templates"),
    [TOOL.GET_PIPELINE_TEMPLATE]:         t("Reading pipeline template"),
    [TOOL.CREATE_PIPELINE_FROM_TEMPLATE]: t("Creating pipeline from template"),
    [TOOL.LIST_STATIC_WEBAPPS]:           t("Listing web apps"),
    [TOOL.CREATE_STATIC_WEBAPP]:          t("Creating web app"),
    [TOOL.UPDATE_STATIC_WEBAPP]:          t("Updating web app"),
    [TOOL.GET_HELP_OR_DOC]:               t("Reading documentation"),
    [TOOL.PROPOSE_PIPELINE_VERSION]:      t("Proposing pipeline version"),
    [TOOL.EXECUTE_GRAPHQL]:               t("Executing GraphQL query"),
  };
}

export function formatToolName(
  toolName: string,
  labels?: Record<string, string>,
): string {
  if (labels?.[toolName]) return labels[toolName];

  for (const [prefix, verb] of PREFIX_VERBS) {
    if (toolName.startsWith(prefix)) {
      const rest = toolName.slice(prefix.length).replace(/_/g, " ");
      return `${verb} ${rest}`;
    }
  }

  return toolName
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}
