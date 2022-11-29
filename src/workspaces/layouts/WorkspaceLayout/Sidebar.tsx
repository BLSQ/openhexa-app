import {
  ArrowPathIcon,
  BookOpenIcon,
  CircleStackIcon,
  Cog6ToothIcon,
  FolderOpenIcon,
  HomeIcon,
  SwatchIcon,
  UserGroupIcon,
} from "@heroicons/react/24/outline";
import { ChevronDownIcon } from "@heroicons/react/24/solid";
import clsx from "clsx";
import Link from "core/components/Link";
import Menu from "core/components/Menu";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { ReactNode, useMemo } from "react";
import { WORKSPACES } from "workspaces/helpers/fixtures";

type SidebarProps = {
  workspaceId: string;
};

const NavItem = (props: {
  icon?: ReactNode;
  children: ReactNode;
  href: string;
  exact?: boolean;
}) => {
  const { icon, children, href, exact } = props;
  const router = useRouter();

  const isCurrent = useMemo(() => {
    if (!exact && router.asPath.startsWith(href)) {
      return true;
    }

    if (exact && router.asPath === href) {
      return true;
    }

    return false;
  }, [href, exact, router.asPath]);

  return (
    <Link
      href={href}
      noStyle
      className={clsx(
        "group flex items-center gap-3 border-l-4 px-2 py-2 text-sm font-medium",
        isCurrent
          ? " border-pink-500 text-white"
          : "border-transparent text-gray-300 hover:bg-gray-700 hover:text-white"
      )}
    >
      {icon && (
        <div
          className={clsx(
            isCurrent
              ? "text-gray-300"
              : "text-gray-400 group-hover:text-gray-300"
          )}
        >
          {icon}
        </div>
      )}
      {children}
    </Link>
  );
};

const Sidebar = (props: SidebarProps) => {
  const { workspaceId } = props;
  const { t } = useTranslation();
  const router = useRouter();
  const workspace = WORKSPACES.find((x) => x.id === workspaceId);
  if (!workspace) {
    return null;
  }
  return (
    <div className="fixed inset-y-0 flex w-64 flex-col">
      <div className="flex flex-grow flex-col overflow-y-auto border-r border-gray-200 bg-gray-800">
        <div className="flex h-16 flex-shrink-0 items-center justify-between py-3 px-4 text-white">
          <Link
            noStyle
            href={`/workspaces/${encodeURIComponent(workspace.id)}`}
            className="flex-1 font-medium"
          >
            {workspace.name}
            <div className="text-sm font-normal text-gray-50 text-opacity-70">
              Country
            </div>
          </Link>
          <Menu trigger={<ChevronDownIcon className="h-6 w-6" />}>
            {WORKSPACES.map((item) => (
              <Menu.Item
                onClick={() =>
                  router.push(`/workspaces/${encodeURIComponent(item.id)}`)
                }
                key={item.id}
              >
                {item.name}
              </Menu.Item>
            ))}
          </Menu>
        </div>
        <div className="mt-5 flex flex-grow flex-col">
          <nav className="flex-1 space-y-1 px-0 pb-4">
            <NavItem
              exact
              href={`/workspaces/${encodeURIComponent(workspaceId)}`}
            >
              <HomeIcon className="h-5 w-5" />
              {t("Home")}
            </NavItem>
            <NavItem
              href={`/workspaces/${encodeURIComponent(workspaceId)}/files`}
            >
              <FolderOpenIcon className="h-5 w-5" />
              {t("Files")}
            </NavItem>
            <NavItem
              href={`/workspaces/${encodeURIComponent(workspaceId)}/databases`}
            >
              <CircleStackIcon className="h-5 w-5" />
              {t("Database")}
            </NavItem>
            <NavItem
              href={`/workspaces/${encodeURIComponent(
                workspaceId
              )}/connections`}
            >
              <SwatchIcon className="h-5 w-5" />
              {t("Connections")}
            </NavItem>
            <NavItem
              href={`/workspaces/${encodeURIComponent(workspaceId)}/pipelines`}
            >
              <ArrowPathIcon className="h-5 w-5" />
              {t("Pipelines")}
            </NavItem>
            <NavItem
              href={`/workspaces/${encodeURIComponent(workspaceId)}/notebooks`}
            >
              <BookOpenIcon className="h-5 w-5" />
              {t("JupyterHub")}
            </NavItem>
            <NavItem
              href={`/workspaces/${encodeURIComponent(workspaceId)}/settings`}
            >
              <Cog6ToothIcon className="h-5 w-5" />
              {t("Settings")}
            </NavItem>
          </nav>
        </div>
        <div className="mb-5 flex flex-shrink-0 flex-col items-center px-4">
          <Link
            noStyle
            href="/dashboard"
            className="relative flex h-8 flex-shrink-0 items-center"
          >
            <img
              className="h-full"
              src="/images/logo_with_text_white.svg"
              alt="OpenHexa logo"
            />
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
