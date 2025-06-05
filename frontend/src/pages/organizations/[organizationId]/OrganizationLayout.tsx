import React, { useState } from "react";
import clsx from "clsx";
import Sidebar from "./Sidebar";
import SpotlightSearch from "core/features/SpotlightSearch/SpotlightSearch";

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

  const toggleSidebar = () => setSidebarOpen((prev) => !prev);

  return (
    <div className="flex h-screen">
      <Sidebar
        organization={organization}
        isSidebarOpen={isSidebarOpen}
        toggleSidebar={toggleSidebar}
      />
      <div
        className={clsx(
          "flex-grow transition-all duration-200",
          isSidebarOpen ? "pl-64" : "pl-16",
        )}
      >
        <SpotlightSearch isSidebarOpen={isSidebarOpen} isMac={false} />
        <main className="p-6">{children}</main>
      </div>
    </div>
  );
};

export default OrganizationLayout;
