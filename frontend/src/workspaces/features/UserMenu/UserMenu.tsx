import { gql, useQuery } from "@apollo/client";
import { Transition } from "@headlessui/react";
import {
  ArrowRightStartOnRectangleIcon,
  Cog6ToothIcon,
  QuestionMarkCircleIcon,
  UserIcon,
} from "@heroicons/react/24/outline";
import clsx from "clsx";
import Link from "core/components/Link";
import Tooltip from "core/components/Tooltip";
import Field from "core/components/forms/Field";
import UserAvatar from "identity/features/UserAvatar";
import UILanguagePicker from "identity/features/UILanguagePicker";
import { logout } from "identity/helpers/auth";
import useFeature from "identity/hooks/useFeature";
import useMe from "identity/hooks/useMe";
import useToggle from "core/hooks/useToggle";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { Fragment, useEffect, useRef, useState } from "react";
import { usePopper } from "react-popper";
import useOnClickOutside from "use-onclickoutside";
import { UserMenuQuery, UserMenuQueryVariables } from "./UserMenu.generated";

interface UserMenuProps {
  compact?: boolean;
}

const POPPER_MODIFIERS = [{ name: "offset", options: { offset: [18, 5] } }];

const UserMenu = (props: UserMenuProps) => {
  const { compact = false } = props;
  const { t } = useTranslation();
  const me = useMe();
  const [hasLegacyAccess] = useFeature("openhexa_legacy");
  const router = useRouter();

  useEffect(() => {
    if (isOpen) {
      setFalse();
    }
  }, [router.asPath]);

  const [isOpen, { toggle, setFalse }] = useToggle();

  const innerMenuRef = useRef<HTMLDivElement>(null);
  const [referenceElement, setReferenceElement] =
    useState<HTMLButtonElement | null>(null);
  const [popperElement, setPopperElement] = useState<HTMLElement | null>(null);
  const { styles, attributes } = usePopper(referenceElement, popperElement, {
    strategy: "fixed",
    placement: "top-start",
    modifiers: POPPER_MODIFIERS,
  });

  useOnClickOutside(innerMenuRef, () => {
    setFalse();
  });

  const { data } = useQuery<UserMenuQuery, UserMenuQueryVariables>(gql`
    query UserMenu {
      pendingWorkspaceInvitations(page: 1, perPage: 1) {
        totalItems
      }
    }
  `);

  if (!me.user) {
    return null;
  }

  return (
    <div className="w-full" ref={innerMenuRef}>
      <button
        className={clsx(
          "group flex w-full items-center bg-gray-800 text-left hover:bg-gray-700 transition-colors",
          compact ? "h-16 justify-center px-2" : "h-auto gap-3 px-3 py-3",
        )}
        ref={setReferenceElement}
        onClick={toggle}
      >
        {compact ? (
          <UserAvatar size="sm" user={me.user} />
        ) : (
          <>
            <UserAvatar size="sm" user={me.user} />
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-gray-50 truncate">
                {me.user.displayName}
              </div>
              <div className="text-xs text-gray-400 truncate">
                {me.user.email}
              </div>
            </div>
          </>
        )}
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
          className="z-50 flex w-64 flex-col divide-y divide-gray-200 rounded-sm bg-white text-base shadow-md ring-1 ring-black/5 focus:outline-hidden"
        >
          <section className="flex justify-center py-3 px-4 bg-gray-50 rounded-t">
            <Link noStyle href="/" className="flex h-7 items-center">
              <img
                className="h-full"
                src="/images/logo_with_text_black.svg"
                alt="OpenHEXA logo"
              />
            </Link>
          </section>
          <section className="flex flex-col text-sm font-normal">
            <Link
              href="/user/account"
              noStyle
              className="group flex gap-2 px-4 py-2.5 text-gray-700 transition-all hover:bg-gray-100 hover:text-gray-800"
            >
              <UserIcon className="h-5 w-5 text-gray-400 transition-all group-hover:text-gray-600" />
              {t("Account settings")}
              {data?.pendingWorkspaceInvitations.totalItems ? (
                <div className="ml-auto">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-pink-500">
                    {data.pendingWorkspaceInvitations.totalItems}
                  </span>
                </div>
              ) : null}
            </Link>
            {me.permissions.adminPanel && (
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
              href="https://docs.openhexa.com/#user-manual"
              noStyle
              className="group flex gap-2 px-4 py-2.5 text-gray-700 transition-all hover:bg-gray-100 hover:text-gray-800"
            >
              <QuestionMarkCircleIcon className="h-5 w-5 text-gray-400 transition-all group-hover:text-gray-600" />
              {t("Documentation")}
            </Link>

            <button
              onClick={() => logout()}
              className="group flex gap-2 px-4 py-2.5 text-red-600 transition-all hover:bg-gray-100 hover:text-gray-800"
            >
              <ArrowRightStartOnRectangleIcon className="h-5 w-5" />
              {t("Sign out")}
            </button>
          </section>

          {hasLegacyAccess && (
            <section className="flex flex-col text-sm font-normal">
              <div className="flex items-center justify-between px-4 py-2 pt-5 text-sm font-medium tracking-wide text-gray-500 opacity-90">
                {t("Deprecated features")}
                <Tooltip
                  label={t(
                    "Features linked here are deprecated and will be removed from OpenHEXA in the coming months",
                  )}
                >
                  <QuestionMarkCircleIcon className="h-4 w-4 text-gray-500" />
                </Tooltip>
              </div>
              <Link
                href="/notebooks"
                noStyle
                className="px-4 py-2.5 text-gray-500 transition-all hover:bg-gray-100 hover:text-gray-800"
              >
                {t("Notebooks")}
              </Link>
              <Link
                href="/pipelines"
                noStyle
                className="px-4 py-2.5 text-gray-500 transition-all hover:bg-gray-100 hover:text-gray-800"
              >
                {t("Airflow pipelines")}
              </Link>
            </section>
          )}

          <section className="px-3 py-3">
            <Field
              name="language"
              labelColor="text-gray-400 font-normal"
              label={t("Interface language")}
              showOptional={false}
            >
              <UILanguagePicker className="w-full" />
            </Field>
          </section>
        </div>
      </Transition>
    </div>
  );
};

export default UserMenu;
