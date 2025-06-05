import React from "react";
import clsx from "clsx";
import Link from "core/components/Link";

type SidebarProps = {
  organization: {
    id: string;
    name: string;
    workspaces: { items: { slug: string; name: string }[] };
  };
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
};

const Sidebar = ({
  organization,
  isSidebarOpen,
  toggleSidebar,
}: SidebarProps) => {
  return (
    <div
      className={clsx(
        "fixed h-full bg-gray-800 transition-all duration-200",
        isSidebarOpen ? "w-64" : "w-16",
      )}
    >
      <div className="flex flex-col h-full">
        <div className="p-4 text-white text-lg font-bold">
          {organization.name}
        </div>
        <nav className="flex-1 space-y-1 px-2">
          {organization.workspaces.items.map((workspace) => (
            <Link
              key={workspace.slug}
              href={`/workspaces/${workspace.slug}`}
              className="block px-4 py-2 text-gray-300 hover:bg-gray-700 hover:text-white"
            >
              {workspace.name}
            </Link>
          ))}
        </nav>
        <button
          onClick={toggleSidebar}
          className="absolute inset-y-0 right-0 bg-gray-700 text-white p-2"
        >
          {isSidebarOpen ? "Collapse" : "Expand"}
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
