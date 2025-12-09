import { gql } from "@apollo/client";
import {
  BoltIcon,
  BookmarkIcon,
  BookOpenIcon,
  ChevronDownIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ChevronUpIcon,
  CircleStackIcon,
  Cog6ToothIcon,
  FolderOpenIcon,
  GlobeAltIcon,
  HomeIcon,
  Square2StackIcon,
  SwatchIcon,
} from "@heroicons/react/24/outline";
import clsx from "clsx";
import Badge from "core/components/Badge";
import Link from "core/components/Link";
import { CustomApolloClient } from "core/helpers/apollo";
import { useTranslation } from "next-i18next";
import React, { useContext, useMemo, useState } from "react";
import SidebarMenu from "workspaces/features/SidebarMenu";
import UserMenu from "workspaces/features/UserMenu";
import { Sidebar_WorkspaceFragment } from "./Sidebar.generated";
import { LayoutContext } from "./WorkspaceLayout";
import { useRouter } from "next/router";
import { GetServerSidePropsContext } from "next";
import SpotlightSearch from "core/features/SpotlightSearch/SpotlightSearch";

type SidebarProps = {
  workspace: Sidebar_WorkspaceFragment;
  className?: string;
};

const NavItem = (props: {
  Icon: any;
  label?: string;
  href: string;
  isCurrent: boolean;
  compact?: boolean;
  className?: string;
}) => {
  const { Icon, compact, label, href, isCurrent, className } = props;

  return (
    <Link
      href={href}
      noStyle
      className={clsx(
        className,
        "text-md group relative flex items-center gap-3 px-2 py-2 font-medium",
        isCurrent
          ? "text-white"
          : " text-gray-300 hover:bg-gray-700 hover:text-white",
        compact && "justify-center ",
      )}
    >
      <div
        className={clsx(
          "absolute inset-y-0 left-0 w-1 bg-pink-500 transition-opacity",
          isCurrent ? "opacity-100" : "opacity-0",
        )}
      ></div>
      <Icon className={clsx(compact ? "h-7 w-7" : "ml-1 h-5 w-5")} />
      {compact ? (
        <div className="absolute inset-y-0 left-full ml-1.5 hidden h-full items-center text-xs opacity-0 transition-opacity group-hover:flex group-hover:opacity-100">
          <Badge className="bg-gray-800 ring-gray-500/20">{label}</Badge>
        </div>
      ) : (
        <span className="whitespace-nowrap overflow-hidden transition-opacity duration-200">
          {label}
        </span>
      )}
    </Link>
  );
};

const Sidebar = (props: SidebarProps) => {
  const { workspace, className } = props;
  const { t } = useTranslation();
  const { isSidebarOpen, setSidebarOpen } = useContext(LayoutContext);
  const [isShortcutsExpanded, setShortcutsExpanded] = useState(true);

  const router = useRouter();

  const { slug, shortcuts } = workspace;

  const homeLink = {
    href: `/workspaces/${encodeURIComponent(slug)}`,
    label: t("Home"),
    Icon: HomeIcon,
  };
  const pipelineLink = {
    href: `/workspaces/${encodeURIComponent(slug)}/pipelines`,
    label: t("Pipelines"),
    Icon: BoltIcon,
  };

  const links = [
    {
      href: `/workspaces/${encodeURIComponent(slug)}/files`,
      label: t("Files"),
      Icon: FolderOpenIcon,
    },
    {
      href: `/workspaces/${encodeURIComponent(slug)}/databases`,
      label: t("Database"),
      Icon: CircleStackIcon,
    },
    {
      href: `/workspaces/${encodeURIComponent(slug)}/datasets`,
      label: t("Datasets"),
      Icon: Square2StackIcon,
    },
    {
      href: `/workspaces/${encodeURIComponent(slug)}/connections`,
      label: t("Connections"),
      Icon: SwatchIcon,
    },
    pipelineLink,
    ...(workspace.permissions.launchNotebookServer
      ? [
          {
            href: `/workspaces/${encodeURIComponent(slug)}/notebooks`,
            label: t("JupyterHub"),
            Icon: BookOpenIcon,
          },
        ]
      : []),
    {
      href: `/workspaces/${encodeURIComponent(slug)}/webapps`,
      label: t("Apps"),
      Icon: GlobeAltIcon,
    },
    ...(workspace.permissions.manageMembers
      ? [
          {
            href: `/workspaces/${encodeURIComponent(slug)}/settings`,
            label: t("Settings"),
            Icon: Cog6ToothIcon,
          },
        ]
      : []),
  ];

  const currentLink = useMemo(() => {
    for (const { href } of links) {
      if (router.asPath.startsWith(href)) {
        return href;
      }
    }
    if (
      router.asPath.startsWith(
        `/workspaces/${encodeURIComponent(slug)}/templates`,
      )
    ) {
      return pipelineLink.href;
    }
    if (router.asPath.startsWith(homeLink.href)) {
      return homeLink.href;
    }
  }, [router.asPath]);

  return (
    <div className={clsx("relative z-20 flex h-full flex-col", className)}>
      <div className="flex h-full grow flex-col border-r border-gray-200 bg-gray-800">
        {workspace.organization && (
          <NavItem
            className="h-16"
            key="organization"
            href={"/organizations/" + workspace.organization.id}
            Icon={ChevronLeftIcon}
            label={
              workspace.organization.shortName ?? workspace.organization.name
            }
            isCurrent={false}
            compact={!isSidebarOpen}
          />
        )}
        <SpotlightSearch isSidebarOpen={isSidebarOpen} />
        <SidebarMenu compact={!isSidebarOpen} workspace={workspace} />

        <div className="mt-5 flex grow flex-col overflow-y-auto scrollbar-visible">
          <nav className="flex-1 space-y-1 px-0 pb-4">
            {[homeLink].concat(links).map(({ href, Icon, label }) => (
              <NavItem
                key={href}
                href={href}
                Icon={Icon}
                label={label}
                isCurrent={currentLink === href}
                compact={!isSidebarOpen}
              />
            ))}

            {shortcuts.length > 0 && (
              <div className="mt-3 border-t border-gray-700 pt-3">
                <button
                  onClick={() => setShortcutsExpanded(!isShortcutsExpanded)}
                  className="flex w-full items-center justify-between px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white rounded-md"
                >
                  <div className="flex items-center gap-2">
                    <BookmarkIcon className="h-4 w-4" />
                    {isSidebarOpen && <span>{t("Shortcuts")}</span>}
                  </div>
                  {isSidebarOpen &&
                    (isShortcutsExpanded ? (
                      <ChevronUpIcon className="h-4 w-4" />
                    ) : (
                      <ChevronDownIcon className="h-4 w-4" />
                    ))}
                </button>

                {isShortcutsExpanded && (
                  <div className="space-y-1 mt-1">
                    {shortcuts.map((shortcut) => (
                      <NavItem
                        key={shortcut.id}
                        href={shortcut.url}
                        Icon={GlobeAltIcon}
                        label={shortcut.name}
                        isCurrent={router.asPath === shortcut.url}
                        compact={!isSidebarOpen}
                        className="pl-6"
                      />
                    ))}
                  </div>
                )}
              </div>
            )}
          </nav>
        </div>

        <UserMenu compact={!isSidebarOpen} />
      </div>
      <button
        onClick={() => setSidebarOpen(!isSidebarOpen)}
        className="group absolute inset-y-0 right-0 border-r-4 border-transparent after:absolute after:inset-y-0 after:-left-1.5 after:block after:w-5 after:content-[''] hover:border-r-gray-500"
      >
        <div className="relative h-full">
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center">
            <div className="pointer-events-auto invisible rounded-l-md bg-gray-500 p-1 pr-0.5 align-middle text-white group-hover:visible">
              {isSidebarOpen ? (
                <ChevronLeftIcon className="h-5 w-5" />
              ) : (
                <ChevronRightIcon className="h-5 w-5" />
              )}
            </div>
          </div>
        </div>
      </button>
    </div>
  );
};

Sidebar.fragments = {
  workspace: gql`
    fragment Sidebar_workspace on Workspace {
      slug
      ...SidebarMenu_workspace
      permissions {
        manageMembers
        update
        launchNotebookServer
      }
      shortcuts {
        id
        name
        url
        order
      }
    }
    ${SidebarMenu.fragments.workspace}
  `,
};

Sidebar.prefetch = async (
  ctx: GetServerSidePropsContext,
  client: CustomApolloClient,
) => {
  await SidebarMenu.prefetch(client);
  await SpotlightSearch.prefetch(ctx);
};

export default Sidebar;
