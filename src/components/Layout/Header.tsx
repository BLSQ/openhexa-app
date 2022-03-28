import { CustomApolloClient } from "libs/apollo";
import Image from "next/image";
import Link from "next/link";
import Navbar from "./Navbar";

const Header = () => {
  return (
    <div className="bg-gray-800">
      <div className="mx-auto flex h-16 max-w-7xl items-center gap-6 px-2 sm:px-6 lg:px-8">
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
        {/* User Menu */}
      </div>
    </div>
  );
};

Header.prefetch = async (client: CustomApolloClient) => {};

export default Header;
