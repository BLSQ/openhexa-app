import { PlusCircleIcon } from "@heroicons/react/24/outline";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import Page from "core/components/Page";
import Title from "core/components/Title";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useState } from "react";
import ConnectionDataCard from "workspaces/features/ConnectionDataCard";
import CreateConnectionDialog from "workspaces/features/CreateConnectionDialog";
import { WORKSPACES } from "workspaces/helpers/fixtures";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  page: number;
  perPage: number;
};

const WorkspaceConnectionsPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const router = useRouter();
  const workspace = WORKSPACES.find((w) => w.id === router.query.workspaceId);
  const [openModal, setOpenModal] = useState(false);

  if (!workspace) {
    return null;
  }

  return (
    <Page title={t("Workspace")}>
      <WorkspaceLayout.Header>
        <Breadcrumbs withHome={false}>
          <Breadcrumbs.Part
            isFirst
            href={`/workspaces/${encodeURIComponent(workspace.id)}`}
          >
            {workspace.name}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part
            href={`/workspaces/${encodeURIComponent(workspace.id)}/connections`}
          >
            {t("Connections")}
          </Breadcrumbs.Part>
        </Breadcrumbs>
      </WorkspaceLayout.Header>
      <WorkspaceLayout.PageContent>
        <div className="flex flex-1 items-center justify-between">
          <Title level={2} className="mb-0">
            Connections
          </Title>
          <div>
            <Button
              leadingIcon={<PlusCircleIcon className="w-6" />}
              onClick={() => setOpenModal(true)}
            >
              {t("Add connection")}
            </Button>
          </div>
        </div>
        <div className="mt-4 grid grid-cols-3 gap-5 sm:grid-cols-3">
          {workspace.connections.map((connection, index) => (
            <div key={index} className="col-sspan-1">
              <ConnectionDataCard
                workspaceId={workspace.id}
                connection={connection}
              />
            </div>
          ))}
        </div>
        <CreateConnectionDialog
          open={openModal}
          onClose={() => setOpenModal(!openModal)}
        />
      </WorkspaceLayout.PageContent>
    </Page>
  );
};

WorkspaceConnectionsPage.getLayout = (page, pageProps) => {
  return <WorkspaceLayout pageProps={pageProps}>{page}</WorkspaceLayout>;
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
});

export default WorkspaceConnectionsPage;
