import clsx from "clsx";
import Avatar from "core/components/Avatar";
import Toggle from "core/helpers/Toggle";
import { MeAuthorizedActions } from "graphql-types";
import { getMe, logout } from "identity/helpers/auth";
import { useTranslation } from "next-i18next";
import Link from "next/link";
import { useRouter } from "next/router";
import Quicksearch from "catalog/features/Quicksearch";
import Menu from "../Menu";
import Navbar from "./Navbar";
import { LayoutClasses } from "./styles";
import { MagnifyingGlassIcon } from "@heroicons/react/24/outline";
import useMe from "identity/hooks/useMe";

const Header = () => {
  const me = useMe();
  const router = useRouter();
  const { t } = useTranslation();
  if (!me.user) {
    return null;
  }
  return (
    <div className="bg-gray-800">
      <div
        className={clsx(
          LayoutClasses.container,
          "flex h-16 items-center gap-6"
        )}
      >
        <Link href="/dashboard">
          <a className="relative flex h-8 flex-shrink-0 items-center">
            <img
              className="block h-full lg:hidden"
              src="/images/logo.svg"
              alt="OpenHexa logo"
            />
            <img
              className="hidden h-full lg:block"
              src="/images/logo_with_text_white.svg"
              alt="OpenHexa logo"
            />
          </a>
        </Link>
        <Navbar />
        <Toggle>
          {({ isToggled, toggle }) => (
            <>
              <a
                className="group mr-4 hidden flex-shrink cursor-pointer items-center space-x-2 text-gray-400 hover:text-white md:inline-flex"
                onClick={toggle}
              >
                <MagnifyingGlassIcon className="h-5" />
                <span>{t("Search")}</span>
                <span className="inline-flex items-center rounded border border-gray-400 p-1 text-xs font-medium shadow-sm focus:outline-none group-hover:border-white">
                  ⌘K
                </span>
              </a>
              <Quicksearch open={isToggled} onClose={toggle} />
            </>
          )}
        </Toggle>
        <Menu
          trigger={
            <Avatar
              initials={me.user?.avatar.initials ?? ""}
              color={me.user ? me.user.avatar.color : undefined}
              size="md"
            />
          }
        >
          <Menu.Item onClick={() => router.push("/user/account")}>
            {t("Your account")}
          </Menu.Item>
          {me.authorizedActions?.includes(MeAuthorizedActions.AdminPanel) && (
            <Menu.Item onClick={() => router.push("/admin")}>
              {t("Admin")}
            </Menu.Item>
          )}

          <Menu.Item onClick={() => logout()}>{t("Sign out")}</Menu.Item>
        </Menu>
      </div>
    </div>
  );
};

export default Header;
