import React, { useState } from "react";
import clsx from "clsx";
import Help from "workspaces/layouts/WorkspaceLayout/Help";
import { useTranslation } from "next-i18next";
import { getCookie, hasCookie, setCookie } from "cookies-next";

export let cookieSidebarOpenState = true;

function getDefaultSidebarOpen() {
  if (typeof window === "undefined") {
    return cookieSidebarOpenState;
  } else if (hasCookie("sidebar-open")) {
    return getCookie("sidebar-open") === "true";
  } else {
    return true;
  }
}

type BaseLayoutProps = {
  children: React.ReactNode;
  Sidebar: React.ElementType;
  sidebarProps: any;
};

const BaseLayout = ({ children, Sidebar, sidebarProps }: BaseLayoutProps) => {
  const [isSidebarOpen, setSidebarOpen] = useState(getDefaultSidebarOpen());
  const { t } = useTranslation();

  const onChangeSidebar = (open: boolean) => {
    setCookie("sidebar-open", open);
    setSidebarOpen(open);
  };

  return (
    <div className="flex h-screen">
      <Sidebar
        {...sidebarProps}
        isSidebarOpen={isSidebarOpen}
        setSidebarOpen={onChangeSidebar}
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

BaseLayout.prefetch = async (ctx: any) => {
  // Load the cookie value from the request to render it correctly on the server
  cookieSidebarOpenState = (await hasCookie("sidebar-open", ctx))
    ? (await getCookie("sidebar-open", ctx)) === "true"
    : true;
};

export default BaseLayout;
