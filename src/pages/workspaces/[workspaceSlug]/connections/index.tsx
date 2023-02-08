import { PlusIcon } from "@heroicons/react/24/outline";
import Badge from "core/components/Badge";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import Card from "core/components/Card";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useState } from "react";
import CreateConnectionDialog from "workspaces/features/CreateConnectionDialog";
import { TYPES } from "workspaces/features/CreateConnectionDialog/CreateConnectionDialog";
import {
  useWorkspaceConnectionsPageQuery,
  WorkspaceConnectionsPageDocument,
} from "workspaces/graphql/queries.generated";
import { FAKE_WORKSPACE } from "workspaces/helpers/fixtures";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  page: number;
  perPage: number;
};

const WorkspaceConnectionsPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const router = useRouter();
  const [openModal, setOpenModal] = useState(false);
  const { data } = useWorkspaceConnectionsPageQuery({
    variables: { workspaceSlug: router.query.workspaceSlug as string },
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

            <Button
              leadingIcon={<PlusIcon className="w-4" />}
              onClick={() => setOpenModal(true)}
            >
              {t("Add connection")}
            </Button>
          </div>
        </WorkspaceLayout.Header>
        <WorkspaceLayout.PageContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4 xl:grid-cols-3 xl:gap-5">
            {FAKE_WORKSPACE.connections.map((connection) => (
              <Card
                key={connection.id}
                title={
                  <div className="flex justify-between gap-2">
                    <>
                      {(() => {
                        const type = TYPES.find(
                          (type) => type.value === connection.type.value
                        );
                        return (
                          type && (
                            <div className="flex items-center gap-x-2">
                              <img
                                src={type.iconSrc}
                                className="h-6 w-6"
                                alt=""
                              />
                              {connection.name}
                            </div>
                          )
                        );
                      })()}
                      <Badge className={connection.type.color}>
                        {connection.type.label}
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
                <Card.Content className="line-clamp-3">
                  {connection.shortDescription}
                </Card.Content>
              </Card>
            ))}
          </div>
        </WorkspaceLayout.PageContent>
      </Page>

      <CreateConnectionDialog
        open={openModal}
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
      query: WorkspaceConnectionsPageDocument,
      variables: { workspaceSlug: ctx.params?.workspaceSlug },
    });

    if (!data.workspace) {
      return {
        notFound: true,
      };
    }
  },
});

export default WorkspaceConnectionsPage;
