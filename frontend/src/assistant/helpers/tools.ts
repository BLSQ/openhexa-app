// Canonical roster of assistant tool machine names — the single source of truth
// for tool identities. Every tool-keyed table (labels in `toolNames`, per-tool
// config in `toolConfig`, renderer overrides) keys off these constants instead
// of repeating the strings, so a name lives in exactly one place. Mirrors the
// backend tools in `hexa/mcp/tools/`; keep in sync when tools are added/renamed.
export const TOOL = {
  LIST_WORKSPACES: "list_workspaces",
  GET_WORKSPACE: "get_workspace",
  LIST_FILES: "list_files",
  READ_FILE: "read_file",
  WRITE_FILE: "write_file",
  LIST_DATASETS: "list_datasets",
  GET_DATASET: "get_dataset",
  PREVIEW_DATASET_FILE: "preview_dataset_file",
  CREATE_DATASET: "create_dataset",
  CREATE_DATASET_VERSION: "create_dataset_version",
  LIST_PIPELINES: "list_pipelines",
  GET_PIPELINE: "get_pipeline",
  GET_PIPELINE_RUN: "get_pipeline_run",
  RUN_PIPELINE: "run_pipeline",
  UPDATE_PIPELINE: "update_pipeline",
  CREATE_PIPELINE: "create_pipeline",
  CREATE_PIPELINE_VERSION: "create_pipeline_version",
  LIST_CONNECTIONS: "list_connections",
  LIST_PIPELINE_TEMPLATES: "list_pipeline_templates",
  GET_PIPELINE_TEMPLATE: "get_pipeline_template",
  CREATE_PIPELINE_FROM_TEMPLATE: "create_pipeline_from_template",
  LIST_STATIC_WEBAPPS: "list_static_webapps",
  CREATE_STATIC_WEBAPP: "create_static_webapp",
  UPDATE_STATIC_WEBAPP: "update_static_webapp",
  GET_HELP_OR_DOC: "get_help_or_doc",
  PROPOSE_PIPELINE_VERSION: "propose_pipeline_version",
  EXECUTE_GRAPHQL: "execute_graphql",
} as const;

export type ToolName = (typeof TOOL)[keyof typeof TOOL];
