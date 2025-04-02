import {
  Button as HeadlessMenuButton,
  Menu as HeadlessMenu,
  MenuItem as HeadlessMenuItem,
  MenuItems as HeadlessMenuItems,
} from "@headlessui/react";
import { ChevronDownIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import { Classes as ButtonClasses } from "./Button/Button";
import { ReactElement, ReactNode } from "react";
import Link from "next/link";

export const MenuClasses = {
  Menu: "relative",
  TriggerButton: clsx(
    "group",
    ButtonClasses.base,
    ButtonClasses.white,
    ButtonClasses.md,
  ),
  Item: "group text-left flex transition px-2 py-2 items-center w-full text-sm rounded-sm hover:bg-blue-500 hover:text-white",
  ActiveItem: "bg-blue-500 text-white",
  Items:
    "origin-top-right  absolute right-0 mt-2 w-36 ring-1 ring-black/5 rounded-sm shadow-lg bg-white text-gray-900 focus:outline-hidden text-right z-40 divide-y divide-gray-200",
};

type MenuProps = {
  label?: string;
  trigger?: ReactElement;
  className?: string;
  children: ReactNode;
};

const Menu = ({ label, trigger, className, children }: MenuProps) => {
  return (
    <HeadlessMenu as="div" className={clsx(MenuClasses.Menu, className)}>
      {trigger ? (
        <HeadlessMenuButton>{trigger}</HeadlessMenuButton>
      ) : (
        <HeadlessMenuButton className={MenuClasses.TriggerButton}>
          {label}
          <ChevronDownIcon
            className="-mr-1 ml-2 h-4 w-4 text-gray-500 group-hover:text-gray-700"
            aria-hidden="true"
          />
        </HeadlessMenuButton>
      )}
      <HeadlessMenuItems className={MenuClasses.Items}>
        <div className="px-1 py-1">{children}</div>
      </HeadlessMenuItems>
    </HeadlessMenu>
  );
};

type ItemProps = {
  children: ReactNode;
  className?: string;
  activeClassName?: string;
} & (
  | {
      onClick: (event: { preventDefault: Function }) => void;
      href?: never;
    }
  | { onClick?: never; href: React.ComponentProps<typeof Link>["href"] }
);

const Item = ({
  children,
  activeClassName = MenuClasses.ActiveItem,
  onClick,
  className = MenuClasses.Item,
  href,
}: ItemProps) => (
  <HeadlessMenuItem>
    {({ focus }) =>
      onClick ? (
        <button
          onClick={onClick}
          className={clsx(className, focus && activeClassName)}
        >
          {children}
        </button>
      ) : (
        <Link href={href} className={clsx(className, focus && activeClassName)}>
          {children}
        </Link>
      )
    }
  </HeadlessMenuItem>
);

Menu.Item = Item;

export default Menu;
