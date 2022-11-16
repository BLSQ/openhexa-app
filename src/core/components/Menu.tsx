import { Menu as HeadlessMenu, Transition } from "@headlessui/react";
import { ChevronDownIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import { Classes as ButtonClasses } from "./Button/Button";
import { Fragment, ReactNode } from "react";
import { ReactElement } from "react-markdown/lib/react-markdown";
import Link from "next/link";

export const MenuClasses = {
  Menu: "relative",
  TriggerButton: clsx(
    "group",
    ButtonClasses.base,
    ButtonClasses.white,
    ButtonClasses.md
  ),
  Item: "group flex transition px-2 py-2 items-center w-full text-sm rounded hover:bg-blue-500 hover:text-white",
  ActiveItem: "bg-blue-500 text-white",
  Items:
    "origin-top-right absolute right-0 mt-2 w-36 ring-1 ring-black ring-opacity-5 rounded shadow-lg bg-white text-gray-900 focus:outline-none text-right z-40 divide-y divide-gray-200 ",
};

const TRANSITION = {
  enter: "transition ease-out duration-100",
  enterFrom: "transform opacity-0 scale-95",
  enterTo: "transform opacity-100 scale-100",
  leave: "transition ease-in duration-75",
  leaveFrom: "transform opacity-100 scale-100",
  leaveTo: "transform opacity-0 scale-95",
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
        <HeadlessMenu.Button>{trigger}</HeadlessMenu.Button>
      ) : (
        <HeadlessMenu.Button className={MenuClasses.TriggerButton}>
          {label}
          <ChevronDownIcon
            className="ml-2 -mr-1 h-4 w-4 text-gray-500 group-hover:text-gray-700"
            aria-hidden="true"
          />
        </HeadlessMenu.Button>
      )}
      <Transition as={Fragment} {...TRANSITION}>
        <HeadlessMenu.Items className={MenuClasses.Items}>
          <div className="px-1 py-1">{children}</div>
        </HeadlessMenu.Items>
      </Transition>
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
  | { onClick?: never; href: string }
);

const Item = ({
  children,
  activeClassName = MenuClasses.ActiveItem,
  onClick,
  className = MenuClasses.Item,
  href,
}: ItemProps) => (
  <HeadlessMenu.Item>
    {({ active }) => (
      <>
        {onClick && (
          <button
            onClick={onClick}
            className={clsx(className, active && activeClassName)}
          >
            {children}
          </button>
        )}

        {href && (
          <Link
            href={href}
            className={clsx(className, active && activeClassName)}
          >
            {children}
          </Link>
        )}
      </>
    )}
  </HeadlessMenu.Item>
);

Menu.Item = Item;

export default Menu;
