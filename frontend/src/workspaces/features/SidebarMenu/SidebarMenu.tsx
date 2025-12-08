import { gql, useQuery } from "@apollo/client";
import { Transition } from "@headlessui/react";
import { GlobeAltIcon } from "@heroicons/react/24/outline";
import { ChevronDownIcon, PlusCircleIcon } from "@heroicons/react/24/solid";
import clsx from "clsx";
import Link from "core/components/Link";
import { CustomApolloClient } from "core/helpers/apollo";
import useCacheKey from "core/hooks/useCacheKey";
import useToggle from "core/hooks/useToggle";
import useMe from "identity/hooks/useMe";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { Fragment, useEffect, useRef, useState } from "react";
import { usePopper } from "react-popper";
import useOnClickOutside from "use-onclickoutside";

import CreateWorkspaceDialog from "../CreateWorkspaceDialog";
import {
  SidebarMenu_WorkspaceFragment,
  SidebarMenuDocument,
  SidebarMenuQuery,
  SidebarMenuQueryVariables,
} from "./SidebarMenu.generated";
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
            </div>
            <ChevronDownIcon className="ml-1 h-4 w-4 text-gray-500 group-hover:text-gray-100" />
          </>
        ) : (
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-gray-700 text-lg font-semibold text-gray-200">
            {workspace.name.charAt(0).toUpperCase()}
          </div>
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
          className="divide z-50 flex w-72 flex-col divide-y divide-gray-200 overflow-x-hidden max-h-9/12 overflow-y-auto rounded-sm bg-white pt-2 text-base shadow-md ring-1 ring-black/5 focus:outline-hidden"
        >
          <section>
            <div className="flex w-full items-center justify-between px-4 py-2 text-sm font-medium tracking-wide text-gray-500 opacity-90">
              {t("Your workspaces")}

              {(me.permissions.createWorkspace ||
                workspace.organization?.permissions.createWorkspace) && (
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
                    organizationId={workspace.organization?.id}
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
      organization {
        id
        name
        shortName
        permissions {
          createWorkspace
        }
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
