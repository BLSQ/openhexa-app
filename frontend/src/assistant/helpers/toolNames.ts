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

// Curated labels for the tools an agent can actually call. Keyed off the
// generated `TOOL` enum, so a renamed or removed tool fails compilation here.
// Tools without an entry fall back to `formatToolName`.
export function getToolLabels(t: TFunction): Record<string, string> {
  return {
    [TOOL.ListFiles]: t("Listing files"),
    [TOOL.ReadFile]: t("Reading file"),
    [TOOL.ListDatasets]: t("Listing datasets"),
    [TOOL.GetDataset]: t("Reading dataset"),
    [TOOL.PreviewDatasetFile]: t("Previewing dataset file"),
    [TOOL.ListConnections]: t("Listing connections"),
    [TOOL.CreatePipeline]: t("Creating pipeline"),
    [TOOL.GetHelpOrDoc]: t("Reading documentation"),
    [TOOL.ProposePipelineVersion]: t("Proposing pipeline version"),
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
