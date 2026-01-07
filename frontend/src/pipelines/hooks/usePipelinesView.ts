import useCookieState from "core/hooks/useCookieState";

export default function usePipelinesView() {
  return useCookieState<"grid" | "card">({
    name: "pipelines-view",
    defaultValue: "grid",
  });
}