import Block from "core/components/Block";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import ChevronLinkColumn from "core/components/DataGrid/ChevronLinkColumn";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import Page from "core/components/Page";
import Link from "core/components/Link";
import { createGetServerSideProps } from "core/helpers/page";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import React, { useMemo, useState } from "react";
import Button from "core/components/Button";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";
import Breadcrumbs from "core/components/Breadcrumbs";
import { PlusIcon, StarIcon } from "@heroicons/react/24/outline";
import {
  useWorkspaceWebappsPageQuery,
  WorkspaceWebappsPageDocument,
  WorkspaceWebappsPageQuery,
  WorkspaceWebappsPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import useCacheKey from "core/hooks/useCacheKey";
import Title from "core/components/Title";
import UserAvatar from "identity/features/UserAvatar";
import clsx from "clsx";
import {
  useAddToFavoritesMutation,
  useRemoveFromFavoritesMutation,
} from "webapps/graphql/mutations.generated";
import { toast } from "react-toastify";
import Spinner from "core/components/Spinner";

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

  const [addToFavorites] = useAddToFavoritesMutation();
  const [removeFromFavorites] = useRemoveFromFavoritesMutation();
  const [settingFavoriteOf, setSettingFavoriteOf] = useState<string | null>();

  const handleFavoriteClick = async (webappId: string, isFavorite: boolean) => {
    try {
      setSettingFavoriteOf(webappId);
      if (isFavorite) {
        await removeFromFavorites({ variables: { input: { webappId } } });
        toast.success(t("Removed from favorites"));
      } else {
        await addToFavorites({ variables: { input: { webappId } } });
        toast.success(t("Added to favorites"));
      }
      refetch();
    } catch (error) {
      toast.error(t("Error updating favorites"));
    } finally {
      setSettingFavoriteOf(null);
    }
  };

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
          <>
            <Breadcrumbs withHome={false} className="flex-1">
              <Breadcrumbs.Part
                isFirst
                href={`/workspaces/${encodeURIComponent(workspace.slug)}`}
              >
                {workspace.name}
              </Breadcrumbs.Part>
              <Breadcrumbs.Part
                isLast
                href={`/workspaces/${encodeURIComponent(
                  workspace.slug,
                )}/webapps`}
              >
                {t("Web Apps")}
              </Breadcrumbs.Part>
            </Breadcrumbs>
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
          </>
        }
      >
        <WorkspaceLayout.PageContent>
          <Title level={2}>{t("All apps")}</Title>
          <Block>
            <DataGrid
              defaultPageSize={perPage}
              data={items}
              totalItems={data.webapps.totalItems}
              fetchData={onChangePage}
            >
              <BaseColumn id="name" label={t("Name")}>
                {(item) => (
                  <div className="flex items-center space-x-1">
                    {settingFavoriteOf === item.id ? (
                      <Spinner size={"xs"} />
                    ) : (
                      <StarIcon
                        data-testid={`star-icon-${item.id}`}
                        className={clsx(
                          "h-5 w-5 cursor-pointer text-yellow-500",
                          item.isFavorite && "fill-yellow-500",
                        )}
                        onClick={() =>
                          handleFavoriteClick(item.id, item.isFavorite)
                        }
                      />
                    )}
                    <img
                      src={item.icon}
                      className={clsx(
                        "h-4 w-4 rounded",
                        !item.icon && "invisible",
                      )}
                      alt={"Icon"}
                    />
                    <Link
                      href={{
                        pathname: `/workspaces/${encodeURIComponent(workspace.slug)}/webapps/${item.id}`,
                      }}
                    >
                      {item.name}
                    </Link>
                  </div>
                )}
              </BaseColumn>
              <BaseColumn id="createdBy" label={t("Created by")}>
                {(item) => (
                  <div className={"flex space-x-1"}>
                    <UserAvatar user={item.createdBy} size="xs" />
                    <p>{item.createdBy.displayName}</p>
                  </div>
                )}
              </BaseColumn>
              <TextColumn label={t("Workspace")} accessor="workspace.name" />
              <ChevronLinkColumn
                accessor="id"
                url={(value: any) => ({
                  pathname: `/workspaces/${encodeURIComponent(workspace.slug)}/webapps/${value}`,
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
