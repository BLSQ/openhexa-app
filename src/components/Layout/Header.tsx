import { SearchIcon } from "@heroicons/react/solid";
import clsx from "clsx";
import Avatar from "components/Avatar";
import Link from "next/link";
import Navbar from "./Navbar";
import { LayoutClasses } from "./styles";

const Header = ({ user }: { user: any }) => {
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
          <span>Search</span>
          <span className="inline-flex items-center rounded border border-gray-400 p-1 text-xs font-medium shadow-sm focus:outline-none group-hover:border-white">
            ⌘K
          </span>
        </a>
        <Avatar
          initials={user.avatar.initials}
          color={user.avatar.color}
          size="md"
        />
      </div>
    </div>
  );
};

export default Header;
