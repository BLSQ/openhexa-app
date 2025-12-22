import { gql } from "@apollo/client";
import clsx from "clsx";
import { CustomApolloClient } from "core/helpers/apollo";
import useLocalStorage from "core/hooks/useLocalStorage";
import SpotlightSearch from "core/features/SpotlightSearch/SpotlightSearch";
import { GetServerSidePropsContext } from "next";
import { ComponentProps, ReactElement, ReactNode, useEffect } from "react";
import Help from "./Help";
import PageContent from "./PageContent";
import Sidebar from "./Sidebar";
import { WorkspaceLayout_WorkspaceFragment } from "./WorkspaceLayout.generated";
import useSidebarOpen from "core/hooks/useSidebarOpen";

export type WorkspaceLayoutProps = {
  children: ReactElement | ReactElement[];
  className?: string;
  workspace: WorkspaceLayout_WorkspaceFragment;
  helpLinks?: ComponentProps<typeof Help>["links"];
  header?: ReactNode;
  headerActions?: ReactNode;
  withMarginBottom?: boolean;
  forceSidebarOpen?: boolean;
  setForceSidebarOpen?: (open: boolean) => void;
};

const WorkspaceLayout = (props: WorkspaceLayoutProps) => {
  const {
    children,
    workspace,
    helpLinks,
    header,
    headerActions,
    className,
    withMarginBottom = true,
    forceSidebarOpen,
    setForceSidebarOpen,
  } = props;
  const [_, setLastWorkspace] = useLocalStorage("last-visited-workspace");

  const [cookieSidebarOpen] = useSidebarOpen();
  const isSidebarOpen = forceSidebarOpen ?? cookieSidebarOpen;

  useEffect(() => {
    setLastWorkspace(workspace.slug);
  }, [workspace.slug, setLastWorkspace]);

  return (
    <>
      <div
        className={clsx(
          "fixed h-screen bg-gray-800 transition-all duration-75 z-20",
          isSidebarOpen ? "w-64 2xl:w-72" : "w-16",
        )}
      >
        <Sidebar
          workspace={workspace}
          forceSidebarOpen={forceSidebarOpen}
          setForceSidebarOpen={setForceSidebarOpen}
        />
      </div>
      {header && (
        <header
          className={clsx(
            "fixed top-0 left-0 right-0 z-10 h-16 border-b border-gray-200 bg-white py-3 shadow-xs group/header",
            isSidebarOpen ? "left-64 2xl:left-72" : "left-16",
          )}
        >
          <div className="flex items-center h-full px-4 md:px-6 xl:px-10 2xl:px-12">
            <div className="flex-1 min-w-0">{header}</div>
            <div className="shrink-0 w-100 max-w-md mx-auto p-2">
              <SpotlightSearch />
            </div>
            <div className="flex-1 flex justify-end items-center gap-2">
              {headerActions}
            </div>
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
    </>
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
  await Sidebar.prefetch(ctx, client);
  await SpotlightSearch.prefetch(ctx);
};

WorkspaceLayout.PageContent = PageContent;
WorkspaceLayout.Help = Help;

export default WorkspaceLayout;
