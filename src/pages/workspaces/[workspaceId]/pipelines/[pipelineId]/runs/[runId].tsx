import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Page from "core/components/Page";
import Title from "core/components/Title";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import PipelineRunOutputEntry from "pipelines/features/PipelineRunOutputEntry";
import PipelineRunStatusBadge from "pipelines/features/PipelineRunStatusBadge";
import { getPipelineRunLabel } from "pipelines/helpers/runs";
import { WORKSPACES } from "workspaces/helpers/fixtures";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  page: number;
  perPage: number;
};

const WorkspacePipelineRunDetailsPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const router = useRouter();
  const workspace = WORKSPACES.find((w) => w.id === router.query.workspaceId);

  if (!workspace) {
    return null;
  }

  const dag = workspace.dags.find((d) => d.id === router.query.pipelineId);

  if (!dag) {
    return null;
  }

  const dagRun = dag.runs.find((r) => r.id === router.query.runId);

  if (!dagRun) {
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
            href={`/workspaces/${encodeURIComponent(workspace.id)}/pipelines}`}
          >
            {t("Pipelines")}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part
            href={`/workspaces/${encodeURIComponent(
              workspace.id
            )}/pipelines/${encodeURIComponent(dag.id)}`}
          >
            {dag.label}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part
            href={{
              pathname: "/pipelines/[pipelineId]/runs/[runId]",
              query: { pipelineId: dag.id, runId: dagRun.id },
            }}
          >
            {getPipelineRunLabel(dagRun, dag)}
          </Breadcrumbs.Part>
        </Breadcrumbs>
      </WorkspaceLayout.Header>
      <WorkspaceLayout.PageContent>
        <Block className="grid grid-cols-3 gap-6 p-4">
          <div className="col-span-3">
            <Title level={2}>
              {t("Run details of {{label}}", { label: dag.label })}
            </Title>
            <div className="flex space-x-4">
              <span> {getPipelineRunLabel(dagRun, dag)}</span>
              <PipelineRunStatusBadge dagRun={dagRun} />
            </div>
          </div>
          <div className="col-span-3">
            <Title level={5}>{t("Outputs")}</Title>
            <div className="flex space-x-2">
              {dagRun.output &&
                dagRun.output.map((output, index) => (
                  <PipelineRunOutputEntry key={index} output={output} />
                ))}
            </div>
          </div>
          <div className="col-span-3">
            <Title level={5}>{t("Configuration")}</Title>
            <p>Parameter 1 : value 1</p>
            <p>Parameter 2 : value 2</p>
          </div>
          <div className="col-span-3">
            <Title level={5}>{t("Logs")}</Title>
            <code>
              <pre className="max-h-36 w-1/2 overflow-y-auto whitespace-pre-line text-xs">
                {dagRun.logs}
              </pre>
            </code>
          </div>
        </Block>
      </WorkspaceLayout.PageContent>
    </Page>
  );
};

WorkspacePipelineRunDetailsPage.getLayout = (page, pageProps) => {
  return <WorkspaceLayout pageProps={pageProps}>{page}</WorkspaceLayout>;
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
});

export default WorkspacePipelineRunDetailsPage;
