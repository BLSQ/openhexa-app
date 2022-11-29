import Breadcrumbs from "core/components/Breadcrumbs";
import Page from "core/components/Page";
import Tabs from "core/components/Tabs";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import PipelineDataCard from "workspaces/features/PipelineDataCard";
import { WORKSPACES } from "workspaces/helpers/fixtures";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  page: number;
  perPage: number;
};

const WorkspacePipelinesPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const router = useRouter();
  const workspace = WORKSPACES.find((w) => w.id === router.query.workspaceId);

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
            href={`/workspaces/${encodeURIComponent(workspace.id)}/pipelines`}
          >
            {t("Pipelines")}
          </Breadcrumbs.Part>
        </Breadcrumbs>
      </WorkspaceLayout.Header>
      <WorkspaceLayout.PageContent>
        <div>
          <Tabs defaultIndex={0}>
            <Tabs.Tab
              className="mt-4 grid grid-cols-2 gap-5 sm:grid-cols-3"
              label={t("All pipelines")}
            >
              {workspace.dags.map((dag, index) => (
                <PipelineDataCard
                  workspaceId={workspace.id}
                  key={index}
                  dag={dag}
                />
              ))}
            </Tabs.Tab>
          </Tabs>
        </div>

        <div></div>
      </WorkspaceLayout.PageContent>
    </Page>
  );
};

WorkspacePipelinesPage.getLayout = (page, pageProps) => {
  return <WorkspaceLayout pageProps={pageProps}>{page}</WorkspaceLayout>;
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
});

export default WorkspacePipelinesPage;
