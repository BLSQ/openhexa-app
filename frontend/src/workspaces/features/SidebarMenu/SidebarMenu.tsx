import { gql, useQuery } from "@apollo/client";
import { Transition } from "@headlessui/react";
import { useAutoAnimate } from "@formkit/auto-animate/react";
import {
  GlobeAltIcon,
  StarIcon as OutlineStarIcon,
} from "@heroicons/react/24/outline";
import {
  ChevronDownIcon,
  PlusCircleIcon,
  StarIcon as SolidStarIcon,
} from "@heroicons/react/24/solid";
import clsx from "clsx";
import Link from "core/components/Link";
import SearchInput from "core/features/SearchInput";
import { CustomApolloClient } from "core/helpers/apollo";
import useCacheKey from "core/hooks/useCacheKey";
import useLocalStorage from "core/hooks/useLocalStorage";
import useToggle from "core/hooks/useToggle";
import useMe from "identity/hooks/useMe";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import React, { Fragment, useEffect, useMemo, useRef, useState } from "react";
import { usePopper } from "react-popper";
import Flag from "react-world-flags";
import useOnClickOutside from "use-onclickoutside";

import CreateWorkspaceDialog from "../CreateWorkspaceDialog";
import {
  SidebarMenu_WorkspaceFragment,
  SidebarMenuDocument,
  SidebarMenuQuery,
  SidebarMenuQueryVariables,
} from "./SidebarMenu.generated";

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
  const [isOpen, { toggle, setFalse }] = useToggle();

  const [search, setSearch] = useState("");
  const searchInputRef = useRef<HTMLInputElement>(null);
  const [favorites, setFavorites] = useLocalStorage<string[]>(
    "workspace-favorites",
    [],
  );

  const [listRef] = useAutoAnimate<HTMLDivElement>({ duration: 200 });
  const [isAnimationReady, setIsAnimationReady] = useState(false);
  // Only enable auto-animate after the menu has rendered to prevent initial flicker
  useEffect(() => {
    if (isOpen) {
      setSearch("");
      setTimeout(() => {
        searchInputRef.current?.focus();
      }, 50);
      // Wait for the menu transition to complete before enabling animations
      const timer = setTimeout(() => setIsAnimationReady(true), 150);
      return () => clearTimeout(timer);
    } else {
      setIsAnimationReady(false);
    }
  }, [isOpen]);

  useEffect(() => {
    if (isOpen) {
      setFalse();
    }
  }, [router.asPath]);

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
      query SidebarMenu($page: Int, $perPage: Int, $organizationId: UUID) {
        workspaces(page: $page, perPage: $perPage, organizationId: $organizationId) {
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
      variables: { page: 1, perPage: 2000, organizationId: workspace.organization?.id },
      fetchPolicy: "cache-and-network",
    },
  );

  useCacheKey("workspaces", () => {
    refetch().then();
  });

  const toggleFavorite = (slug: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (favorites.includes(slug)) {
      setFavorites(favorites.filter((s) => s !== slug));
    } else {
      setFavorites([...favorites, slug]);
    }
  };

  const sortedWorkspaces = useMemo(() => {
    if (!data?.workspaces.items) return [];

    let filtered = data.workspaces.items;

    if (search.trim()) {
      const searchLower = search.toLowerCase().trim();
      filtered = filtered.filter((ws) =>
        ws.name.toLowerCase().includes(searchLower),
      );
    }

    // Sort: favorites first, then alphabetical
    return [...filtered].sort((a, b) => {
      const aFav = favorites.includes(a.slug);
      const bFav = favorites.includes(b.slug);
      if (aFav && !bFav) return -1;
      if (!aFav && bFav) return 1;
      return a.name.localeCompare(b.name);
    });
  }, [data?.workspaces.items, favorites, search]);

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
          <div className="flex h-10 w-10 items-center justify-center rounded-md text-lg font-semibold text-gray-200">
            {workspace.countries.length === 1 ? (
              <Flag
                code={workspace.countries[0].code}
                className="w-5 h-4 shrink rounded-xs"
              />
            ) : (
              workspace.name.charAt(0).toUpperCase()
            )}
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
            <div className="flex w-full items-center gap-2 px-2 py-2 justify-between">
              <SearchInput
                ref={searchInputRef}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={t("Search workspaces...")}
                className="flex-1"
                fullWidth
              />
              {(me.permissions.createWorkspace ||
                workspace.organization?.permissions.createWorkspace) && (
                <>
                  <button
                    type="button"
                    onClick={() => setDialogOpen(true)}
                    title={t("Create a new workspace")}
                    className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
                  >
                    <PlusCircleIcon className="h-5 w-5" />
                  </button>
                  <CreateWorkspaceDialog
                    open={isDialogOpen}
                    onClose={() => setDialogOpen(false)}
                    organizationId={workspace.organization?.id}
                  />
                </>
              )}
            </div>

            <div
              ref={isAnimationReady ? listRef : undefined}
              className="max-h-96 overflow-y-auto"
            >
              {sortedWorkspaces.map((ws) => {
                const isFavorite = favorites.includes(ws.slug);
                return (
                  <Link
                    noStyle
                    href={{
                      pathname: "/workspaces/[workspaceSlug]",
                      query: { workspaceSlug: ws.slug },
                    }}
                    className={clsx(
                      "group/item flex items-center px-4 py-2.5 hover:bg-gray-100",
                      ws.slug === workspace.slug && "font-semibold",
                    )}
                    key={ws.slug}
                  >
                    <div className="mr-2.5 flex h-full w-5 shrink-0 items-center">
                      {ws.countries && ws.countries.length === 1 ? (
                        <Flag
                          code={ws.countries[0].code}
                          className="w-5 shrink rounded-xs"
                        />
                      ) : (
                        <GlobeAltIcon className="w-5 shrink rounded-xs text-gray-400" />
                      )}
                    </div>
                    <span className="flex-1 text-sm leading-tight tracking-tight">
                      {ws.name}
                    </span>
                    <button
                      onClick={(e) => toggleFavorite(ws.slug, e)}
                      className="relative ml-2 flex h-6 w-6 shrink-0 items-center justify-center rounded-full transition-all duration-200 hover:bg-amber-50 active:scale-75"
                      title={
                        isFavorite
                          ? t("Remove from favorites")
                          : t("Add to favorites")
                      }
                    >
                      <SolidStarIcon
                        className={clsx(
                          "h-4 w-4 transition-all duration-200",
                          isFavorite
                            ? "scale-100 text-amber-400"
                            : "scale-0 text-amber-400",
                        )}
                      />
                      <OutlineStarIcon
                        className={clsx(
                          "absolute h-4 w-4 transition-all duration-200",
                          isFavorite
                            ? "scale-0 text-gray-300"
                            : "scale-100 text-gray-300 group-hover/item:text-gray-400",
                        )}
                      />
                    </button>
                  </Link>
                );
              })}
              {sortedWorkspaces.length === 0 && search.trim() && (
                <div className="px-4 py-3 text-center text-sm text-gray-500">
                  {t("No workspaces found")}
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
        logo
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
    variables: { page: 1, perPage: 2000 },
  });
};

export default SidebarMenu;
