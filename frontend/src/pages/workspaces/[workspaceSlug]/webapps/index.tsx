import Block from "core/components/Block";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import ChevronLinkColumn from "core/components/DataGrid/ChevronLinkColumn";
import Page from "core/components/Page";
import Link from "core/components/Link";
import { createGetServerSideProps } from "core/helpers/page";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import React, { useMemo } from "react";
import Button from "core/components/Button";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";
import Breadcrumbs from "core/components/Breadcrumbs";
import { PlayIcon, PlusIcon } from "@heroicons/react/24/outline";
import {
  useWorkspaceWebappsPageQuery,
  WorkspaceWebappsPageDocument,
  WorkspaceWebappsPageQuery,
  WorkspaceWebappsPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import useCacheKey from "core/hooks/useCacheKey";
import Title from "core/components/Title";
import UserAvatar from "identity/features/UserAvatar";
import FavoriteWebappButton from "webapps/features/FavoriteWebappButton";
import ShortcutWebappButton from "webapps/features/ShortcutWebappButton";
import LinkColumn from "core/components/DataGrid/LinkColumn";
import clsx from "clsx";
import WebappCard from "webapps/features/WebappCard";

type Props = {
  page: number;
  perPage: number;
  workspaceSlug: string;
};

const WebappsPage = (props: Props) => {
  const { page, perPage, workspaceSlug } = props;

  const { t } = useTranslation();
  const router = useRouter();

  const { data, refetch } = useWorkspaceWebappsPageQuery({
    variables: { workspaceSlug, page, perPage },
  });
  useCacheKey("webapps", refetch);

  const onChangePage = ({ page }: { page: number }) => {
    refetch({ page }).then();
  };

  const items = useMemo(() => {
    return data?.webapps.items ?? [];
  }, [data]);

  if (!data?.workspace) {
    return null;
  }

  const { workspace } = data;

  return (
    <Page title={t("Web Apps")}>
      <WorkspaceLayout
        workspace={workspace}
        header={
          <Breadcrumbs withHome={false} className="flex-1">
            <Breadcrumbs.Part
              isFirst
              isLast
              href={`/workspaces/${encodeURIComponent(workspace.slug)}/webapps`}
            >
              {t("Web Apps")}
            </Breadcrumbs.Part>
          </Breadcrumbs>
        }
        headerActions={
          <Button
            leadingIcon={<PlusIcon className="h-4 w-4" />}
            onClick={() =>
              router.push(
                `/workspaces/${encodeURIComponent(workspace.slug)}/webapps/create`,
              )
            }
          >
            {t("Create")}
          </Button>
        }
      >
        <WorkspaceLayout.PageContent>
          {data.favoriteWebapps.items.length > 0 && (
            <>
              <div
                className={clsx(
                  "grid gap-4 mb-6",
                  `grid-cols-${data.favoriteWebapps.items.length}`,
                )}
              >
                {data.favoriteWebapps.items.map((webapp) => (
                  <WebappCard key={webapp.id} webapp={webapp} />
                ))}
              </div>
              <Title level={2}>{t("All apps")}</Title>
            </>
          )}
          <Block>
            <DataGrid
              defaultPageSize={perPage}
              data={items}
              totalItems={data.webapps.totalItems}
              fetchData={onChangePage}
            >
              <BaseColumn id="name" label={t("Name")} minWidth={200} maxWidth={350}>
                {(item) => (
                  <div className="flex items-center space-x-1">
                    <div className="flex items-center space-x-1 flex-shrink-0">
                      <FavoriteWebappButton webapp={item} />
                      <ShortcutWebappButton webapp={item} />
                      <img
                        src={item.icon}
                        className={clsx(
                          "h-4 w-4 rounded",
                          !item.icon && "invisible",
                        )}
                        alt={"Icon"}
                      />
                    </div>
                    <Link
                      href={{
                        pathname: `/workspaces/${encodeURIComponent(workspace.slug)}/webapps/${item.slug}`,
                      }}
                      className="truncate"
                    >
                      {item.name}
                    </Link>
                  </div>
                )}
              </BaseColumn>
              <LinkColumn
                id="play"
                url={(item) => ({
                  pathname: `/workspaces/${encodeURIComponent(workspace.slug)}/webapps/${item.slug}/play`,
                })}
                width={80}
                className={"flex items-center justify-center"}
              >
                <div
                  className={
                    "flex items-center justify-center bg-blue-500 rounded-full h-8 w-8 hover:bg-blue-600 cursor-pointer hover:scale-110"
                  }
                >
                  <PlayIcon className="h-4 w-4 text-white fill-white translate-x-0.25" />
                </div>
              </LinkColumn>
              <BaseColumn id="createdBy" label={t("Created by")}>
                {(item) => (
                  <div className={"flex space-x-1"}>
                    <UserAvatar user={item.createdBy} size="xs" />
                    <p>{item.createdBy.displayName}</p>
                  </div>
                )}
              </BaseColumn>
              <ChevronLinkColumn
                accessor="slug"
                customLabel={t("Details")}
                url={(slug) => ({
                  pathname: `/workspaces/${encodeURIComponent(workspace.slug)}/webapps/${slug}`,
                })}
              />
            </DataGrid>
          </Block>
        </WorkspaceLayout.PageContent>
      </WorkspaceLayout>
    </Page>
  );
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  getServerSideProps: async (ctx, client) => {
    await WorkspaceLayout.prefetch(ctx, client);
    const { workspaceSlug } = ctx.params!;
    const page = (ctx.query.page as string)
      ? parseInt(ctx.query.page as string, 10)
      : 1;
    const perPage = 15;

    await client.query<
      WorkspaceWebappsPageQuery,
      WorkspaceWebappsPageQueryVariables
    >({
      query: WorkspaceWebappsPageDocument,
      variables: {
        workspaceSlug: workspaceSlug as string,
        page,
        perPage,
      },
    });
    return {
      props: {
        workspaceSlug,
        page,
        perPage,
      },
    };
  },
});

export default WebappsPage;
