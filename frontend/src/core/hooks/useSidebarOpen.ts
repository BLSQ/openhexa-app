import useCookieState from "./useCookieState";

export default function useSidebarOpen() {
  return useCookieState<boolean>({
    name: "sidebar-open",
    defaultValue: true,
  });
}
