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
import SubscriptionBanner, {
  useSubscriptionBannerOffsetStyle,
} from "organizations/features/SubscriptionBanner";

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
  const subscriptionBannerOffsetStyle = useSubscriptionBannerOffsetStyle(
    workspace.organization,
  );
  const isSidebarOpen = forceSidebarOpen ?? cookieSidebarOpen;

  useEffect(() => {
    setLastWorkspace(workspace.slug);
  }, [workspace.slug, setLastWorkspace]);

  return (
    <div style={subscriptionBannerOffsetStyle}>
      <SubscriptionBanner organization={workspace.organization} />
      <div
        className={clsx(
          "fixed top-(--subscription-banner-height) h-[calc(100vh-var(--subscription-banner-height))] bg-gray-800 transition-all duration-75 z-20",
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
            "fixed top-(--subscription-banner-height) left-0 right-0 z-10 h-16 border-b border-gray-200 bg-white py-3 shadow-xs group/header",
            isSidebarOpen ? "left-64 2xl:left-72" : "left-16",
          )}
        >
          <div className="flex items-center h-full gap-2 px-4 md:px-6 xl:px-10 2xl:px-12">
            <div className="flex-1 min-w-24 xl:min-w-48">{header}</div>
            <div className="shrink basis-auto max-w-md p-2 xl:basis-80 xl:min-w-48 2xl:basis-100">
              <SpotlightSearch organizationId={workspace.organization?.id} />
            </div>
            <div className="flex-1 flex justify-end items-center gap-2">
              {headerActions}
            </div>
          </div>
        </header>
      )}
      <main
        className={clsx(
          "w-full mt-(--subscription-banner-height)",
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
    </div>
  );
};

WorkspaceLayout.fragments = {
  workspace: gql`
    fragment WorkspaceLayout_workspace on Workspace {
      slug
      organization {
        ...SubscriptionBanner_organization
      }
      ...Sidebar_workspace
    }
    ${Sidebar.fragments.workspace}
    ${SubscriptionBanner.fragments.organization}
  `,
};

WorkspaceLayout.prefetch = async (
  ctx: GetServerSidePropsContext,
  client: CustomApolloClient,
) => {
  await SpotlightSearch.prefetch(ctx);
};

WorkspaceLayout.PageContent = PageContent;
WorkspaceLayout.Help = Help;

export default WorkspaceLayout;
