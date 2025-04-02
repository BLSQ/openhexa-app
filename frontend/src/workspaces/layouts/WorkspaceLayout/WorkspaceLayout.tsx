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
  ReactNode,
  useEffect,
  useState,
} from "react";
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
  header?: ReactNode | ReactNode[];
  headerClassName?: string;
  withMarginBottom?: boolean;
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
    workspace,
    forceCompactSidebar = false,
    helpLinks,
    header,
    className,
    headerClassName = "flex items-center justify-between",
    withMarginBottom = true,
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
      <div
        className={clsx(
          "fixed h-screen bg-gray-800 transition-all duration-75 z-20",
          isSidebarOpen ? "w-64 2xl:w-72" : "w-16",
        )}
      >
        <Sidebar workspace={workspace} />
      </div>
      {header && (
        <header
          className={clsx(
            "fixed top-0 left-0 right-0 z-10 h-16 border-b border-gray-200 bg-white py-3 shadow-xs group/header",
            isSidebarOpen ? "left-64 2xl:left-72" : "left-16",
          )}
        >
          <div
            className={clsx(
              "px-4 md:px-6 xl:px-10 2xl:px-12 h-full gap-2",
              headerClassName,
            )}
          >
            {header}
          </div>
        </header>
      )}
      <main
        className={clsx(
          "w-full",
          withMarginBottom
            ? "mb-12" // The margin bottom is to avoid the Help button to hide the content of the page while at the bottom
            : "",
          isSidebarOpen ? "pl-64 2xl:pl-72" : "pl-16",
          header && "pt-16",
          className,
        )}
      >
        {children}
      </main>

      <div className="fixed bottom-6 right-6">
        <Help links={helpLinks}>
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-white text-3xl shadow-xl ring-1 ring-gray-500/5 transition-all hover:bg-gray-50 hover:text-4xl">
            ?
          </div>
        </Help>
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
WorkspaceLayout.Help = Help;

export default WorkspaceLayout;
