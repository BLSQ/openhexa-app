import React from "react";
import BaseLayout from "organizations/layouts/BaseLayout";
import NoWorkspaceSidebar from "./NoWorkspaceSidebar";

type NoWorkspaceLayoutProps = {
  children?: React.ReactNode;
};

const NoWorkspaceLayout = ({ children }: NoWorkspaceLayoutProps) => {
  return (
    <BaseLayout sidebar={<NoWorkspaceSidebar />}>{children}</BaseLayout>
  );
};

export default NoWorkspaceLayout;