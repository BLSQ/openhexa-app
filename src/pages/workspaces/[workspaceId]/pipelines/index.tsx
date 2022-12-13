import { PlusIcon } from "@heroicons/react/24/outline";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import PipelineCard from "workspaces/features/PipelineCard";
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
      <WorkspaceLayout.Header className="flex items-center gap-2">
        <Breadcrumbs withHome={false} className="flex-1">
          <Breadcrumbs.Part
            isFirst
            href={`/workspaces/${encodeURIComponent(workspace.id)}`}
          >
            {workspace.name}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part
            isLast
            href={`/workspaces/${encodeURIComponent(workspace.id)}/pipelines`}
          >
            {t("Pipelines")}
          </Breadcrumbs.Part>
        </Breadcrumbs>
        <Button leadingIcon={<PlusIcon className="h-4 w-4" />}>
          {t("Create")}
        </Button>
      </WorkspaceLayout.Header>
      <WorkspaceLayout.PageContent>
        <div className="grid grid-cols-2 gap-4 xl:grid-cols-3 xl:gap-5">
          {workspace.dags.map((dag, index) => (
            <PipelineCard workspaceId={workspace.id} key={index} dag={dag} />
          ))}
        </div>
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
