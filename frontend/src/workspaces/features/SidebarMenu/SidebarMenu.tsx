import { gql, useQuery } from "@apollo/client";
import { Transition } from "@headlessui/react";
import {
  ArrowRightOnRectangleIcon,
  Cog6ToothIcon,
  GlobeAltIcon,
  QuestionMarkCircleIcon,
  UserIcon,
} from "@heroicons/react/24/outline";
import { ChevronDownIcon, PlusCircleIcon } from "@heroicons/react/24/solid";
import clsx from "clsx";
import Link from "core/components/Link";
import User from "core/features/User";
import { CustomApolloClient } from "core/helpers/apollo";
import useCacheKey from "core/hooks/useCacheKey";
import useToggle from "core/hooks/useToggle";
import useFeature from "identity/hooks/useFeature";
import useMe from "identity/hooks/useMe";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { Fragment, useEffect, useRef, useState } from "react";
import { usePopper } from "react-popper";
import useOnClickOutside from "use-onclickoutside";

import UserAvatar from "identity/features/UserAvatar";
import CreateWorkspaceDialog from "../CreateWorkspaceDialog";
import {
  SidebarMenu_WorkspaceFragment,
  SidebarMenuDocument,
  SidebarMenuQuery,
  SidebarMenuQueryVariables,
} from "./SidebarMenu.generated";
import { logout } from "identity/helpers/auth";
import Tooltip from "core/components/Tooltip";
import UILanguagePicker from "identity/features/UILanguagePicker";
import Field from "core/components/forms/Field";
import Flag from "react-world-flags";

interface SidebarMenuProps {
  workspace: SidebarMenu_WorkspaceFragment;
  compact?: boolean;
}
const POPPER_MODIFIERS = [{ name: "offset", options: { offset: [8, 4] } }];

const SidebarMenu = (props: SidebarMenuProps) => {
  const { workspace, compact = false } = props;
  const { t } = useTranslation();
  const me = useMe();
  const [isDialogOpen, setDialogOpen] = useState(false);
  const [hasLegacyAccess] = useFeature("openhexa_legacy");
  const router = useRouter();
  useEffect(() => {
    if (isOpen) {
      setFalse();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router.asPath]);

  const [isOpen, { toggle, setFalse }] = useToggle();

  const innerMenuRef = useRef<HTMLDivElement>(null);
  const [referenceElement, setReferenceElement] =
    useState<HTMLButtonElement | null>(null);
  const [popperElement, setPopperElement] = useState<HTMLElement | null>(null);
  const { styles, attributes } = usePopper(referenceElement, popperElement, {
    strategy: "fixed",
    placement: "bottom-start",
    modifiers: POPPER_MODIFIERS,
  });
  useOnClickOutside(innerMenuRef, () => {
    if (!isDialogOpen) {
      // Do not close the menu if the user click in the dialog
      setFalse();
    }
  });

  const { data, refetch } = useQuery<
    SidebarMenuQuery,
    SidebarMenuQueryVariables
  >(
    gql`
      query SidebarMenu($page: Int, $perPage: Int) {
        pendingWorkspaceInvitations(page: 1, perPage: 1) {
          totalItems
        }
        workspaces(page: $page, perPage: $perPage) {
          totalItems
          items {
            slug
            name
            countries {
              code
              flag
            }
          }
        }
      }
    `,
    {
      variables: { page: 1, perPage: 5 },
    },
  );

  useCacheKey("workspaces", () => {
    refetch();
  });

  const showMore = () => {
    refetch({
      page: 1,
      perPage: data?.workspaces.totalItems,
    });
  };

  if (!workspace) {
    return null;
  }

  return (
    <div className="w-full" ref={innerMenuRef}>
      <button
        className="group flex h-16 w-full items-center justify-center bg-gray-800 px-2 text-left hover:bg-gray-600"
        ref={setReferenceElement}
        onClick={toggle}
      >
        {!compact ? (
          <>
            {workspace.countries.length === 1 && (
              <div className="mr-2.5 flex h-full items-center">
                <Flag
                  code={workspace.countries[0].code}
                  className="w-5 h-4 shrink rounded-xs"
                />
              </div>
            )}
            <div
              className={clsx(
                "line-clamp-2 flex-1 text-sm tracking-tight text-gray-50",
              )}
              title={workspace.name}
            >
              {workspace.name}
              {me.user && (
                <div className="text-xs tracking-tighter text-gray-500 group-hover:text-gray-400">
                  {me.user.email}
                </div>
              )}
              {/* This will be pushed outside of the block if there is not enough space to display it */}
            </div>
            <ChevronDownIcon className="ml-1 h-4 w-4 text-gray-500 group-hover:text-gray-100" />
          </>
        ) : me.user ? (
          <UserAvatar size="sm" user={me.user} />
        ) : (
          <UserIcon className="h-6 w-6 text-gray-500" />
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
          className="divide z-50 flex w-72 flex-col divide-y divide-gray-200 overflow-hidden rounded-sm bg-white pt-2 text-base shadow-md ring-1 ring-black/5 focus:outline-hidden"
        >
          <section>
            <div className="flex w-full items-center justify-between px-4 py-2 text-sm font-medium tracking-wide text-gray-500 opacity-90">
              {t("Your workspaces")}

              {me.permissions.createWorkspace && (
                <>
                  <button
                    type="button"
                    onClick={() => setDialogOpen(true)}
                    title={t("Create a new workspace")}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <PlusCircleIcon className="h-5 w-5 " />
                  </button>
                  <CreateWorkspaceDialog
                    open={isDialogOpen}
                    onClose={() => setDialogOpen(false)}
                  />
                </>
              )}
            </div>

            <div className="max-h-96 overflow-y-auto">
              {data?.workspaces.items.map((ws, index) => (
                <Link
                  noStyle
                  href={{
                    pathname: "/workspaces/[workspaceSlug]",
                    query: { workspaceSlug: ws.slug },
                  }}
                  className={clsx(
                    "flex items-center px-4 py-2.5 hover:bg-gray-100",
                    ws.slug === workspace.slug && "bg-gray-100 font-medium",
                  )}
                  key={index}
                >
                  <div className="mr-2.5 flex h-full w-5 items-center">
                    {ws.countries && ws.countries.length === 1 ? (
                      <Flag
                        code={ws.countries[0].code}
                        className="w-5 shrink rounded-xs"
                      />
                    ) : (
                      <GlobeAltIcon className="w-5 shrink rounded-xs text-gray-400" />
                    )}
                  </div>
                  <span className="text-sm leading-tight tracking-tight">
                    {ws.name}
                  </span>
                </Link>
              ))}
              {data?.workspaces.totalItems !==
                data?.workspaces.items.length && (
                <div className="pb-2 text-center">
                  <button
                    onClick={() => showMore()}
                    className="ml-4 inline-flex items-center gap-1 text-sm text-blue-500 hover:text-blue-400"
                  >
                    {t("Show more")}
                  </button>
                </div>
              )}
            </div>
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
              href="https://github.com/BLSQ/openhexa/wiki/User-manual"
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
              <ArrowRightOnRectangleIcon className="h-5 w-5" />
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

          {me.user && (
            <>
              <section className=" px-3 py-3">
                <Field
                  name="language"
                  labelColor="text-gray-400 font-normal"
                  label={t("Interface language")}
                  showOptional={false}
                >
                  <UILanguagePicker className="w-2/" />
                </Field>
              </section>
              <section className="bg-gray-100 px-3 py-3">
                <User textColor="text-gray-600" user={me.user} subtext />
              </section>
            </>
          )}
        </div>
      </Transition>
    </div>
  );
};

SidebarMenu.fragments = {
  workspace: gql`
    fragment SidebarMenu_workspace on Workspace {
      slug
      name
      countries {
        flag
        code
      }
    }
  `,
};

SidebarMenu.prefetch = async (client: CustomApolloClient) => {
  await client.query({
    query: SidebarMenuDocument,
    variables: { page: 1, perPage: 5 },
  });
};

export default SidebarMenu;
