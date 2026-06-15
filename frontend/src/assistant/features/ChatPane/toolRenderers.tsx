import { ReactNode } from "react";
import JsonView from "core/components/JsonView";

export type ToolValueRendererProps = {
  value: unknown;
  kind: "input" | "output";
  toolName: string;
  success: boolean;
};

export type ToolValueRenderer = (props: ToolValueRendererProps) => ReactNode;

const DefaultRenderer: ToolValueRenderer = ({ value }) => <JsonView value={value} />;

// Per-tool overrides. Add an entry here to give a specific tool a humanized view
// of its input/output without touching the generic rendering path (open/closed).
const REGISTRY: Record<string, ToolValueRenderer> = {};

export function resolveToolRenderer(toolName: string): ToolValueRenderer {
  return REGISTRY[toolName] ?? DefaultRenderer;
}
