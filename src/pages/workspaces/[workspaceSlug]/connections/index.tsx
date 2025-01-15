import { PlusIcon } from "@heroicons/react/24/outline";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import Card from "core/components/Card";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import { useState } from "react";
import CreateConnectionDialog from "workspaces/features/CreateConnectionDialog";
import {
  ConnectionsPageDocument,
  useConnectionsPageQuery,
} from "workspaces/graphql/queries.generated";
import Connections from "workspaces/helpers/connections";
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
      <Page title={workspace.name}>
        <WorkspaceLayout
          workspace={workspace}
          helpLinks={[
            {
              label: t("About connections"),
              href: "https://github.com/BLSQ/openhexa/wiki/User-manual#adding-and-managing-connections",
            },
            {
              label: t("Using connections in notebooks"),
              href: "https://github.com/BLSQ/openhexa/wiki/Using-notebooks-in-OpenHEXA#using-connections",
            },
            {
              label: t("Using connections in pipelines"),
              href: "https://github.com/BLSQ/openhexa/wiki/Writing-OpenHEXA-pipelines#using-connections",
            },
          ]}
          header={
            <>
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
                    workspace.slug,
                  )}/connections`}
                >
                  {t("Connections")}
                </Breadcrumbs.Part>
              </Breadcrumbs>

              {workspace.permissions.createConnection && (
                <Button
                  leadingIcon={<PlusIcon className="w-4" />}
                  onClick={() => setOpenModal(true)}
                >
                  {t("Add connection")}
                </Button>
              )}
            </>
          }
        >
          <WorkspaceLayout.PageContent className="space-y-4">
            {workspace.connections.length === 0 ? (
              <div className="text-center text-gray-500">
                <div>{t("This workspace does not have any connection.")}</div>
                {workspace.permissions.createConnection && (
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
                      <div className="flex items-center gap-x-2">
                        {Connections[connection.type].iconSrc && (
                          <img
                            src={Connections[connection.type].iconSrc!}
                            className="h-6 w-6"
                            alt=""
                          />
                        )}
                        {connection.name}
                      </div>
                    }
                    subtitle={Connections[connection.type].label}
                    href={{
                      pathname:
                        "/workspaces/[workspaceSlug]/connections/[connectionId]",
                      query: {
                        workspaceSlug: workspace.slug,
                        connectionId: connection.id,
                      },
                    }}
                  >
                    <Card.Content className="mt-3 line-clamp-3 text-sm">
                      {connection.description}
                    </Card.Content>
                  </Card>
                ))}
              </div>
            )}
          </WorkspaceLayout.PageContent>
        </WorkspaceLayout>
      </Page>

      <CreateConnectionDialog
        open={openModal}
        workspace={workspace}
        onClose={() => setOpenModal(!openModal)}
      />
    </>
  );
};

WorkspaceConnectionsPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await WorkspaceLayout.prefetch(ctx, client);
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
