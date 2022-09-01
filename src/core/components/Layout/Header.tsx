import { SearchIcon } from "@heroicons/react/solid";
import clsx from "clsx";
import Avatar from "core/components/Avatar";
import { logout } from "identity/helpers/auth";
import { useTranslation } from "next-i18next";
import Link from "next/link";
import { useRouter } from "next/router";
import Menu from "../Menu";
import Navbar from "./Navbar";
import { LayoutClasses } from "./styles";

const Header = ({ user }: { user: any }) => {
  const router = useRouter();
  const { t } = useTranslation();
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
        <a className="group mr-4 hidden flex-shrink cursor-pointer items-center space-x-2 text-gray-400 hover:text-white md:inline-flex">
          <SearchIcon className="h-5" />
          <span>{t("Search")}</span>
          <span className="inline-flex items-center rounded border border-gray-400 p-1 text-xs font-medium shadow-sm focus:outline-none group-hover:border-white">
            ⌘K
          </span>
        </a>
        <Menu
          trigger={
            <Avatar
              initials={user.avatar.initials}
              color={user.avatar.color}
              size="md"
            />
          }
        >
          <Menu.Item onClick={() => router.push("/user/account")}>
            {t("Your account")}
          </Menu.Item>
          {/* This needs to be behind a Me.permissions.admin
          <Menu.Item onClick={() => router.push("/admin")}>
            {t("Admin")}
        </Menu.Item> */}

          <Menu.Item onClick={() => logout()}>{t("Sign out")}</Menu.Item>
        </Menu>
      </div>
    </div>
  );
};

export default Header;
