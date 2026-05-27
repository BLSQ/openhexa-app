const OVERRIDES: Record<string, string> = {
  get_help_or_doc: "Reading documentation",
  execute_graphql: "Executing GraphQL query",
};

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

export function formatToolName(toolName: string): string {
  if (OVERRIDES[toolName]) return OVERRIDES[toolName];

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
