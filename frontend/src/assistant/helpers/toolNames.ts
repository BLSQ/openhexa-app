import type { TFunction } from "i18next";

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
    list_workspaces:                t("Listing workspaces"),
    get_workspace:                  t("Reading workspace"),
    list_files:                     t("Listing files"),
    read_file:                      t("Reading file"),
    write_file:                     t("Writing file"),
    list_datasets:                  t("Listing datasets"),
    get_dataset:                    t("Reading dataset"),
    preview_dataset_file:           t("Previewing dataset file"),
    create_dataset:                 t("Creating dataset"),
    create_dataset_version:         t("Creating dataset version"),
    list_pipelines:                 t("Listing pipelines"),
    get_pipeline:                   t("Reading pipeline"),
    get_pipeline_run:               t("Reading pipeline run"),
    run_pipeline:                   t("Running pipeline"),
    update_pipeline:                t("Updating pipeline"),
    create_pipeline:                t("Creating pipeline"),
    create_pipeline_version:        t("Creating pipeline version"),
    list_connections:               t("Listing connections"),
    list_pipeline_templates:        t("Listing pipeline templates"),
    get_pipeline_template:          t("Reading pipeline template"),
    create_pipeline_from_template:  t("Creating pipeline from template"),
    list_static_webapps:            t("Listing web apps"),
    create_static_webapp:           t("Creating web app"),
    update_static_webapp:           t("Updating web app"),
    get_help_or_doc:                t("Reading documentation"),
    propose_pipeline_version:       t("Proposing pipeline version"),
    execute_graphql:                t("Executing GraphQL query"),
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
