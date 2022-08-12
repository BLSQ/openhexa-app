import clsx from "clsx";
import Link from "next/link";
import { useRouter } from "next/router";
import { ReactNode } from "react";

const Classes = {
  item: "px-3 py-2 rounded-md hover:bg-gray-700 hover:text-white text-gray-300",
  activeItem:
    "px-3 py-2 rounded-md hover:bg-gray-700 hover:text-white bg-gray-900 text-white",
};

const Item = ({ href, children }: { href: string; children: ReactNode }) => {
  const router = useRouter();
  return (
    <Link href={href}>
      <a
        className={clsx(
          router.asPath === href ? Classes.activeItem : Classes.item
        )}
      >
        {children}
      </a>
    </Link>
  );
};

const Navbar = () => {
  return (
    <nav className="relative flex flex-1 items-center space-x-4 text-sm font-medium">
      <Item href="/">Dashboard</Item>
      <Item href="/collections">Collections</Item>
      <Item href="/catalog">Catalog</Item>
      <Item href="/notebooks">Notebooks</Item>
      <Item href="/pipelines">Pipelines</Item>
      <Item href="/visualizations">Visualizations</Item>
    </nav>
  );
};

export default Navbar;
