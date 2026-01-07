import useCookieState from "core/hooks/useCookieState";

export default function usePipelineTemplatesView() {
  return useCookieState<"grid" | "card">({
    name: "pipeline-templates-view",
    defaultValue: "grid",
  });
}