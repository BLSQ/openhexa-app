import useCookieState from "core/hooks/useCookieState";

export default function useWorkspacesView() {
  return useCookieState<"grid" | "card">({
    name: "workspaces-view",
    defaultValue: "card",
  });
}