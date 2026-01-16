import React from "react";
import clsx from "clsx";
import Help from "workspaces/layouts/WorkspaceLayout/Help";
import SpotlightSearch from "core/features/SpotlightSearch/SpotlightSearch";
import { useTranslation } from "next-i18next";
import useSidebarOpen from "core/hooks/useSidebarOpen";

type BaseLayoutProps = {
  children: React.ReactNode;
  sidebar: React.ReactNode;
  organizationId?: string;
  header?: React.ReactNode;
  headerActions?: React.ReactNode;
};

const BaseLayout = ({
  children,
  sidebar,
  organizationId,
  header,
  headerActions,
}: BaseLayoutProps) => {
  const { t } = useTranslation();

  const [isSidebarOpen] = useSidebarOpen();

  return (
    <div className="flex h-screen">
      <div
        className={clsx(
          "fixed h-screen bg-gray-800 transition-all duration-75 z-20",
          isSidebarOpen ? "w-64 2xl:w-72" : "w-16",
        )}
      >
        {sidebar}
      </div>
      {organizationId && (
        <header
          className={clsx(
            "fixed top-0 left-0 right-0 z-10 h-16 border-b border-gray-200 bg-white py-3 shadow-xs group/header",
            isSidebarOpen ? "left-64 2xl:left-72" : "left-16",
          )}
        >
          <div className="flex items-center h-full px-4 md:px-6 xl:px-10 2xl:px-12">
            <div className="flex-1 min-w-0">{header}</div>
            <div className="shrink-0 w-100 max-w-md mx-auto p-2">
              <SpotlightSearch organizationId={organizationId} />
            </div>
            <div className="flex-1 flex justify-end items-center gap-2">
              {headerActions}
            </div>
          </div>
        </header>
      )}
      <main
        className={clsx(
          "w-full mb-12 transition-all duration-75",
          isSidebarOpen ? "pl-64 2xl:pl-72" : "pl-16",
          organizationId && header && "pt-12",
        )}
      >
        <div className="py-6 xl:py-8">
          <div className="mx-auto px-4 md:px-6 xl:px-10 2xl:px-12 mt-4">
            {children}
          </div>
        </div>
      </main>
      <div className="fixed bottom-6 right-6">
        <Help
          links={[
            {
              label: t("User manual"),
              href: "https://docs.openhexa.com/#user-manual",
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

BaseLayout.prefetch = async (ctx: any) => {
  await SpotlightSearch.prefetch(ctx);
};

export default BaseLayout;
