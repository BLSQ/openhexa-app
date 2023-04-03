import { gql } from "@apollo/client";
import clsx from "clsx";
import { CustomApolloClient } from "core/helpers/apollo";
import useLocalStorage from "core/hooks/useLocalStorage";
import { ReactElement, useEffect } from "react";
import Header from "./Header";
import PageContent from "./PageContent";
import Sidebar from "./Sidebar";
import { WorkspaceLayout_WorkspaceFragment } from "./WorkspaceLayout.generated";

type WorkspaceLayoutProps = {
  children: ReactElement | ReactElement[];
  className?: string;
  workspace: WorkspaceLayout_WorkspaceFragment;
};

const WorkspaceLayout = (props: WorkspaceLayoutProps) => {
  const { children, className, workspace } = props;

  const [lastWorkspace, setLastWorkspace] = useLocalStorage(
    "last-visited-workspace"
  );
  useEffect(() => {
    setLastWorkspace(workspace.slug);
  }, [workspace.slug, setLastWorkspace]);

  return (
    <>
      <Sidebar workspace={workspace} />
      <main className={clsx("flex flex-col pl-64", className)}>{children}</main>
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

WorkspaceLayout.prefetch = async (client: CustomApolloClient) => {
  await Sidebar.prefetch(client);
};

WorkspaceLayout.PageContent = PageContent;
WorkspaceLayout.Header = Header;

export default WorkspaceLayout;
