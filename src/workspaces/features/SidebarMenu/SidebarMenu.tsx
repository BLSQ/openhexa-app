import { Transition } from "@headlessui/react";
import {
  ArrowRightOnRectangleIcon,
  Cog6ToothIcon,
  UserIcon,
  XCircleIcon,
} from "@heroicons/react/24/outline";
import { ChevronDownIcon, PlusCircleIcon } from "@heroicons/react/24/solid";
import clsx from "clsx";
import Link from "core/components/Link";
import User from "core/features/User";
import useToggle from "core/hooks/useToggle";
import useFeature from "identity/hooks/useFeature";
import useMe from "identity/hooks/useMe";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { Fragment, useEffect, useRef, useState } from "react";
import { usePopper } from "react-popper";
import useOnClickOutside from "use-onclickoutside";

import { WORKSPACES } from "workspaces/helpers/fixtures";

type SidebarMenuProps = {
  workspace: typeof WORKSPACES[0];
};

const POPPER_MODIFIERS = [{ name: "offset", options: { offset: [8, 4] } }];

const SidebarMenu = (props: SidebarMenuProps) => {
  const { workspace } = props;
  const { t } = useTranslation();
  const me = useMe();
  const isAdmin = useFeature("adminPanel");

  const [isOpen, { toggle, setFalse }] = useToggle();
  const router = useRouter();

  const [referenceElement, setReferenceElement] =
    useState<HTMLButtonElement | null>(null);
  const [popperElement, setPopperElement] = useState<HTMLElement | null>(null);
  const { styles, attributes } = usePopper(referenceElement, popperElement, {
    strategy: "fixed",
    placement: "bottom-start",
    modifiers: POPPER_MODIFIERS,
  });
  const innerMenuRef = useRef<HTMLDivElement>(null);
  useOnClickOutside(innerMenuRef, () => {
    setFalse();
  });
  useEffect(() => {
    if (isOpen) {
      setFalse();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router.asPath]);

  return (
    <div className="w-full" ref={innerMenuRef}>
      <button
        className="group flex h-16 w-full items-center bg-gray-800 px-2 text-left hover:bg-gray-600"
        ref={setReferenceElement}
        onClick={toggle}
      >
        {workspace.country && (
          <div className="mr-2.5 flex h-full items-center">
            <img
              alt="Country flag"
              className="w-5 flex-shrink rounded-sm"
              src={`/static/flags/${workspace.country.code}.gif`}
            />
          </div>
        )}
        <div
          className={clsx(
            "tight flex-1 truncate text-sm text-gray-50",
            workspace.name.length < 30 ? "tracking-tight" : "tracking-tighter"
          )}
          title={workspace.name}
        >
          {workspace.name}
          {me.user && (
            <div className="text-xs tracking-tighter text-gray-500 group-hover:text-gray-400">
              {me.user.email}
            </div>
          )}
        </div>
        <ChevronDownIcon className="ml-1 h-4 w-4 text-gray-500 group-hover:text-gray-100" />
      </button>

      <Transition
        show={isOpen}
        as={Fragment}
        enter="transition ease-out duration-100"
        enterFrom="transform opacity-0 scale-95"
        enterTo="transform opacity-100 scale-100"
        leave="transition ease-in duration-75"
        leaveFrom="transform opacity-100 scale-100"
        leaveTo="transform opacity-0 scale-95"
      >
        <div
          style={styles.popper}
          ref={setPopperElement}
          {...attributes.popper}
          className="divide flex w-72 flex-col divide-y divide-gray-200 overflow-hidden rounded bg-white pt-2 text-base shadow-md ring-1 ring-black ring-opacity-5 focus:outline-none"
        >
          <section>
            <div className="flex w-full items-center justify-between px-4 py-2 text-sm font-medium tracking-wide text-gray-500 opacity-90">
              {t("Your workspaces")}
              <button
                type="button"
                title={t("Create a new workspace")}
                className="text-gray-400 hover:text-gray-600"
              >
                <PlusCircleIcon className="h-5 w-5 " />
              </button>
            </div>

            {WORKSPACES.map((item) => (
              <Link
                noStyle
                href={{
                  pathname: "/workspaces/[workspaceId]",
                  query: { workspaceId: item.id },
                }}
                className="flex items-center py-2.5 px-4 hover:bg-gray-100"
                key={item.id}
              >
                {item.country && (
                  <div className="mr-2.5 flex h-full items-center">
                    <img
                      alt="Country flag"
                      className="h-4 flex-shrink rounded-sm"
                      src={`/static/flags/${item.country.code}.gif`}
                    />
                  </div>
                )}
                <span className="text-sm leading-tight tracking-tight">
                  {item.name}
                </span>
              </Link>
            ))}
            {false && (
              <div className="text-center">
                <button
                  type="button"
                  className="pb-2  text-xs font-normal  text-gray-500"
                >
                  {t("See all")}
                </button>
              </div>
            )}
          </section>

          <section className="flex flex-col text-sm font-normal">
            <Link
              href="/user/account"
              noStyle
              className="group flex gap-2 px-4 py-2.5 text-gray-700 transition-all hover:bg-gray-100 hover:text-gray-800"
            >
              <UserIcon className="h-5 w-5 text-gray-400 transition-all group-hover:text-gray-600" />
              {t("Account settings")}
            </Link>
            {isAdmin && (
              <Link
                href="/admin"
                noStyle
                className="group flex gap-2 px-4 py-2.5 text-gray-700 transition-all hover:bg-gray-100 hover:text-gray-800"
              >
                <Cog6ToothIcon className="h-5 w-5 text-gray-400 transition-all group-hover:text-gray-600" />
                {t("Administration")}
              </Link>
            )}
            <Link
              href="/dashboard"
              noStyle
              className="group flex gap-2 px-4 py-2.5 text-gray-700 transition-all hover:bg-gray-100 hover:text-gray-800"
            >
              <XCircleIcon className="h-5 w-5 text-gray-400 transition-all group-hover:text-gray-600" />
              {t("Exit preview")}
            </Link>
            <Link
              href="/logout"
              noStyle
              className="group flex gap-2 px-4 py-2.5 text-red-600 transition-all hover:bg-gray-100 hover:text-gray-800"
            >
              <ArrowRightOnRectangleIcon className="h-5 w-5" />
              {t("Sign out")}
            </Link>
          </section>

          {me.user && (
            <section className="bg-gray-100 px-3 py-3">
              <User textColor="text-gray-600" user={me.user} subtext />
            </section>
          )}
        </div>
      </Transition>
    </div>
  );
};

export default SidebarMenu;
