import React, { useState } from "react";
import Sidebar from "./Sidebar";

type OrganizationLayoutProps = {
  children: React.ReactNode;
  organization: {
    id: string;
    name: string;
    workspaces: { items: { slug: string; name: string }[] };
  };
};

const OrganizationLayout = ({
  children,
  organization,
}: OrganizationLayoutProps) => {
  const [isSidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen">
      <Sidebar
        organization={organization}
        isSidebarOpen={isSidebarOpen}
        setSidebarOpen={(newValue) => setSidebarOpen(newValue)}
      />
      <main className="p-6">{children}</main>
    </div>
  );
};

export default OrganizationLayout;
