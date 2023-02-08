import { LinkIcon, PlusIcon } from "@heroicons/react/24/outline";
import Badge from "core/components/Badge";
import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import Card from "core/components/Card";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import ChevronLinkColumn from "core/components/DataGrid/ChevronLinkColumn";
import DateColumn from "core/components/DataGrid/DateColumn";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import Link from "core/components/Link";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { Connection } from "graphql-types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useState } from "react";
import CreateConnectionDialog from "workspaces/features/CreateConnectionDialog";
import {
  ConnectionsPageDocument,
  useConnectionsPageQuery,
} from "workspaces/graphql/queries.generated";
import { CONNECTION_TYPES } from "workspaces/helpers/connection";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  workspaceSlug: string;
};

const WorkspaceConnectionsPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const [openModal, setOpenModal] = useState(false);
  const { data } = useConnectionsPageQuery({
    variables: { workspaceSlug: props.workspaceSlug },
  });

  if (!data?.workspace) {
    return null;
  }
  const { workspace } = data;
  return (
    <>
      <Page title={t("Workspace")}>
        <WorkspaceLayout.Header>
          <div className="flex items-center justify-between">
            <Breadcrumbs withHome={false}>
              <Breadcrumbs.Part
                isFirst
                href={`/workspaces/${encodeURIComponent(workspace.slug)}`}
              >
                {workspace.name}
              </Breadcrumbs.Part>
              <Breadcrumbs.Part
                isLast
                href={`/workspaces/${encodeURIComponent(
                  workspace.slug
                )}/connections`}
              >
                {t("Connections")}
              </Breadcrumbs.Part>
            </Breadcrumbs>

            {workspace.permissions.update && (
              <Button
                leadingIcon={<PlusIcon className="w-4" />}
                onClick={() => setOpenModal(true)}
              >
                {t("Add connection")}
              </Button>
            )}
          </div>
        </WorkspaceLayout.Header>
        <WorkspaceLayout.PageContent className="space-y-4">
          {workspace.connections.length === 0 ? (
            <div className="text-center text-gray-500">
              <div>{t("This workspace does not have any connection.")}</div>
              {workspace.permissions.update && (
                <Button
                  variant="secondary"
                  onClick={() => setOpenModal(true)}
                  className="mt-4"
                >
                  {t("Create a connection")}
                </Button>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-4 xl:grid-cols-3 xl:gap-5">
              {workspace.connections.map((connection) => (
                <Card
                  key={connection.id}
                  title={
                    <div className="flex justify-between gap-3">
                      <>
                        <div className="flex items-center gap-x-2">
                          {CONNECTION_TYPES[connection.type].iconSrc && (
                            <img
                              src={CONNECTION_TYPES[connection.type].iconSrc!}
                              className="h-6 w-6"
                              alt=""
                            />
                          )}
                          {connection.name}
                        </div>
                        <Badge
                          className={CONNECTION_TYPES[connection.type].color}
                        >
                          {CONNECTION_TYPES[connection.type].label}
                        </Badge>
                      </>
                    </div>
                  }
                  href={{
                    pathname:
                      "/workspaces/[workspaceSlug]/connections/[connectionId]",
                    query: {
                      workspaceSlug: workspace.slug,
                      connectionId: connection.id,
                    },
                  }}
                >
                  <Card.Content className="mt-3 text-sm line-clamp-3">
                    {connection.description}
                  </Card.Content>
                </Card>
              ))}
            </div>
          )}
        </WorkspaceLayout.PageContent>
      </Page>

      <CreateConnectionDialog
        open={openModal}
        workspace={workspace}
        onClose={() => setOpenModal(!openModal)}
      />
    </>
  );
};

WorkspaceConnectionsPage.getLayout = (page, pageProps) => {
  return <WorkspaceLayout pageProps={pageProps}>{page}</WorkspaceLayout>;
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    const { data } = await client.query({
      query: ConnectionsPageDocument,
      variables: { workspaceSlug: ctx.params?.workspaceSlug },
    });

    if (!data.workspace) {
      return {
        notFound: true,
      };
    }
    return {
      props: {
        workspaceSlug: ctx.params?.workspaceSlug,
      },
    };
  },
});

export default WorkspaceConnectionsPage;
