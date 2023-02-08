import clsx from "clsx";
import { useRouter } from "next/router";
import type { ReactElement } from "react";
import Header from "./Header";
import PageContent from "./PageContent";
import Sidebar from "./Sidebar";

type WorkspaceLayoutProps = {
  children: ReactElement;
  mainClassName?: string;
  pageProps: any;
};

const WorkspaceLayout = (props: WorkspaceLayoutProps) => {
  const { children, mainClassName } = props;
  const router = useRouter();

  const workspaceSlug = router.query.workspaceSlug as string;

  if (!workspaceSlug) {
    return null;
  }

  return (
    <>
      <Sidebar workspaceSlug={workspaceSlug} />
      <main className={clsx("flex flex-col pl-64", mainClassName)}>
        {children}
      </main>
    </>
  );
};

WorkspaceLayout.PageContent = PageContent;
WorkspaceLayout.Header = Header;

export default WorkspaceLayout;
