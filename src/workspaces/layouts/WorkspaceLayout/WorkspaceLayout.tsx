import { gql } from "@apollo/client";
import clsx from "clsx";
import { CustomApolloClient } from "core/helpers/apollo";
import useLocalStorage from "core/hooks/useLocalStorage";
import { createContext, ReactElement, useEffect, useState } from "react";
import Header from "./Header";
import PageContent from "./PageContent";
import Sidebar from "./Sidebar";
import { WorkspaceLayout_WorkspaceFragment } from "./WorkspaceLayout.generated";
import { getCookie, setCookie } from "cookies-next";
import { GetServerSidePropsContext } from "next";
type WorkspaceLayoutProps = {
  children: ReactElement | ReactElement[];
  className?: string;
  workspace: WorkspaceLayout_WorkspaceFragment;
  forceCompactSidebar?: boolean;
};

export const LayoutContext = createContext({
  isSidebarOpen: false,
  setSidebarOpen: (open: boolean) => {},
});

export let cookieSidebarOpenState = true;

function getDefaultSidebarOpen() {
  if (typeof window === "undefined") {
    return cookieSidebarOpenState;
  } else {
    return (getCookie("sidebar-open") as boolean) ?? true;
  }
}

const WorkspaceLayout = (props: WorkspaceLayoutProps) => {
  const { children, className, workspace, forceCompactSidebar = false } = props;
  const [_, setLastWorkspace] = useLocalStorage("last-visited-workspace");
  const defaultSidebarOpen = getDefaultSidebarOpen();

  const [isSidebarOpen, setSidebarOpen] = useState(
    !forceCompactSidebar && defaultSidebarOpen
  );

  useEffect(() => {
    setLastWorkspace(workspace.slug);
  }, [workspace.slug, setLastWorkspace]);

  const onChangeSidebar = (open: boolean) => {
    if (!forceCompactSidebar) {
      setCookie("sidebar-open", open);
    }
    setSidebarOpen(open);
  };

  return (
    <LayoutContext.Provider
      value={{
        isSidebarOpen,
        setSidebarOpen: onChangeSidebar,
      }}
    >
      <div className="flex min-h-screen">
        <div className="h-screen bg-gray-800">
          <Sidebar
            workspace={workspace}
            className={clsx(
              "sticky top-0 flex flex-col transition-all duration-75",
              isSidebarOpen ? "w-64 2xl:w-72" : "w-16"
            )}
          />
        </div>

        <main
          className={clsx("flex flex-1 flex-col transition-all", className)}
        >
          {children}
        </main>
      </div>
    </LayoutContext.Provider>
  );
};

WorkspaceLayout.fragments = {
  workspace: gql`
    fragment WorkspaceLayout_workspace on Workspace {
      slug
      ...Sidebar_workspace
    }
    ${Sidebar.fragments.workspace}
  `,
};

WorkspaceLayout.prefetch = async (
  ctx: GetServerSidePropsContext,
  client: CustomApolloClient
) => {
  // Load the cookie value from the request to render it correctly on the server
  cookieSidebarOpenState = (getCookie("sidebar-open", ctx) as boolean) ?? true;
  await Sidebar.prefetch(client);
};

WorkspaceLayout.PageContent = PageContent;
WorkspaceLayout.Header = Header;

export default WorkspaceLayout;
