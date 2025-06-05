import React, { useState } from "react";
import Sidebar from "./Sidebar";
import clsx from "clsx";
import Help from "workspaces/layouts/WorkspaceLayout/Help";
import { useTranslation } from "next-i18next";

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
  const { t } = useTranslation();

  return (
    <div className="flex h-screen">
      <Sidebar
        organization={organization}
        isSidebarOpen={isSidebarOpen}
        setSidebarOpen={(newValue) => setSidebarOpen(newValue)}
      />
      <main
        className={clsx(
          "w-full mb-12",
          isSidebarOpen ? "pl-64 2xl:pl-72" : "pl-16",
        )}
      >
        {children}
      </main>

      <div className="fixed bottom-6 right-6">
        <Help
          links={[
            {
              label: t("User manual"),
              href: "https://github.com/BLSQ/openhexa/wiki/User-manual",
            },
          ]}
        >
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-white text-3xl shadow-xl ring-1 ring-gray-500/5 transition-all hover:bg-gray-50 hover:text-4xl">
            ?
          </div>
        </Help>
      </div>
    </div>
  );
};

export default OrganizationLayout;
