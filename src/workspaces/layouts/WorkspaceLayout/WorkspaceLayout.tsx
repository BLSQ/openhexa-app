import { gql } from "@apollo/client";
import clsx from "clsx";
import { getCookie, hasCookie, setCookie } from "cookies-next";
import { CustomApolloClient } from "core/helpers/apollo";
import useLocalStorage from "core/hooks/useLocalStorage";
import { GetServerSidePropsContext } from "next";
import {
  ComponentProps,
  createContext,
  ReactElement,
  useEffect,
  useState,
} from "react";
import Header from "./Header";
import Help from "./Help";
import PageContent from "./PageContent";
import Sidebar from "./Sidebar";
import { WorkspaceLayout_WorkspaceFragment } from "./WorkspaceLayout.generated";

export type WorkspaceLayoutProps = {
  children: ReactElement | ReactElement[];
  className?: string;
  workspace: WorkspaceLayout_WorkspaceFragment;
  forceCompactSidebar?: boolean;
  helpLinks?: ComponentProps<typeof Help>["links"];
};

export const LayoutContext = createContext<{
  isSidebarOpen: boolean;
  setSidebarOpen(open: boolean): void;
}>({
  isSidebarOpen: false,
  setSidebarOpen: (open: boolean) => {},
});

export let cookieSidebarOpenState = true;

function getDefaultSidebarOpen() {
  if (typeof window === "undefined") {
    return cookieSidebarOpenState;
  } else if (hasCookie("sidebar-open")) {
    return getCookie("sidebar-open") === "true";
  } else {
    return true;
  }
}

const WorkspaceLayout = (props: WorkspaceLayoutProps) => {
  const {
    children,
    className,
    workspace,
    forceCompactSidebar = false,
    helpLinks,
  } = props;
  const [_, setLastWorkspace] = useLocalStorage("last-visited-workspace");
  const defaultSidebarOpen = getDefaultSidebarOpen();

  const [isSidebarOpen, setSidebarOpen] = useState(
    !forceCompactSidebar && defaultSidebarOpen,
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
      <div className="flex min-h-screen w-screen">
        <div
          className={clsx(
            "fixed h-screen bg-gray-800 transition-all duration-75 z-20",
            isSidebarOpen ? "w-64 2xl:w-72" : "w-16",
          )}
        >
          <Sidebar workspace={workspace} />
        </div>
        <div
          className={clsx(
            "w-full transition-all duration-75",
            isSidebarOpen ? "pl-64 2xl:pl-72" : "pl-16",
          )}
        >
          <main
            className={clsx(
              "flex flex-1 flex-col transition-all mb-12", // The margin bottom is to avoid the Help button to hide the content of the page while at the bottom
              className,
            )}
          >
            {children}
          </main>
        </div>

        <div className="fixed bottom-6 right-6">
          <Help links={helpLinks}>
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-white text-3xl shadow-xl ring-1 ring-gray-500 ring-opacity-5 transition-all hover:bg-gray-50 hover:text-4xl">
              ?
            </div>
          </Help>
        </div>
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
  client: CustomApolloClient,
) => {
  // Load the cookie value from the request to render it correctly on the server
  cookieSidebarOpenState = (await hasCookie("sidebar-open", ctx))
    ? (await getCookie("sidebar-open", ctx)) === "true"
    : true;
  await Sidebar.prefetch(client);
};

WorkspaceLayout.PageContent = PageContent;
WorkspaceLayout.Header = Header;
WorkspaceLayout.Help = Help;

export default WorkspaceLayout;
