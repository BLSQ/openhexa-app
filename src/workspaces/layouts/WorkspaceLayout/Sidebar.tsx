import { gql } from "@apollo/client";
import {
  BoltIcon,
  BookOpenIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  CircleStackIcon,
  Cog6ToothIcon,
  FolderOpenIcon,
  HomeIcon,
  Square2StackIcon,
  SwatchIcon,
} from "@heroicons/react/24/outline";
import clsx from "clsx";
import Badge from "core/components/Badge";
import Link from "core/components/Link";
import { CustomApolloClient } from "core/helpers/apollo";
import { useTranslation } from "next-i18next";
import { useContext, useMemo } from "react";
import SidebarMenu from "workspaces/features/SidebarMenu";
import { Sidebar_WorkspaceFragment } from "./Sidebar.generated";
import { LayoutContext } from "./WorkspaceLayout";
import { useRouter } from "next/router";

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
}) => {
  const { Icon, compact, label, href, isCurrent } = props;

  return (
    <Link
      href={href}
      noStyle
      className={clsx(
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
        label
      )}
    </Link>
  );
};

const Sidebar = (props: SidebarProps) => {
  const { workspace, className } = props;
  const { t } = useTranslation();
  const { isSidebarOpen, setSidebarOpen } = useContext(LayoutContext);
  const router = useRouter();

  const { slug } = workspace;

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
        <SidebarMenu compact={!isSidebarOpen} workspace={workspace} />

        <div className="mt-5 flex grow flex-col">
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
          </nav>
        </div>

        <div className="mb-5 flex shrink-0 flex-col items-center px-4">
          <Link noStyle href="/" className="flex h-8 items-center">
            <img
              className="h-full"
              src={
                isSidebarOpen
                  ? "/images/logo_with_text_white.svg"
                  : "/images/logo.svg"
              }
              alt="OpenHEXA logo"
            />
          </Link>
        </div>
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
    }
    ${SidebarMenu.fragments.workspace}
  `,
};

Sidebar.prefetch = async (client: CustomApolloClient) => {
  await SidebarMenu.prefetch(client);
};

export default Sidebar;
