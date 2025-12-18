import { useCookies } from "react-cookie";

export default function useSidebarOpen() {
  const [cookies, setCookie] = useCookies(["sidebar-open"]);
  const isSidebarOpen = cookies["sidebar-open"];
  const setSidebarOpen = (open: boolean) => setCookie("sidebar-open", open);

  return [isSidebarOpen, setSidebarOpen] as const;
}
