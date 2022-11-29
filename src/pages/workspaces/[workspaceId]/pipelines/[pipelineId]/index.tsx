import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import Input from "core/components/forms/Input";
import Page from "core/components/Page";
import Tabs from "core/components/Tabs";
import Title from "core/components/Title";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { capitalize } from "lodash";
import { useTranslation } from "next-i18next";
import Link from "next/link";
import { useRouter } from "next/router";
import { PipelineDataCardStatus } from "workspaces/features/PipelineDataCard/PipelineDataCard";
import { WORKSPACES } from "workspaces/helpers/fixtures";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  page: number;
  perPage: number;
};

const WorkspacePipelinePage: NextPageWithLayout = (props: Props) => {
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
          <Breadcrumbs.Part
            href={`/workspaces/${encodeURIComponent(
              workspace.id
            )}/pipelines/${encodeURIComponent(dag.id)}`}
          >
            {dag.label}
          </Breadcrumbs.Part>
        </Breadcrumbs>
      </WorkspaceLayout.Header>
      <WorkspaceLayout.PageContent>
        <div>
          <Title level={2}>{dag.label}</Title>
          <div className="flex items-end justify-between">
            <p className="w-2/4 truncate text-sm text-gray-700">
              {dag.description}
            </p>
            <Link
              className="flex items-end space-x-2 text-blue-500 text-blue-500"
              href={{
                pathname: `/workspaces/${encodeURIComponent(
                  workspace.id
                )}/pipelines/[pipelineId]/run`,
                query: { pipelineId: dag.id },
              }}
            >
              <Button className="w-20"> {t("Run")} </Button>
            </Link>
          </div>
        </div>
        <Block className="mt-5 p-4">
          <Tabs defaultIndex={0}>
            <Tabs.Tab className="mt-4" label={t("Description")}>
              <div>
                <Title level={5}>{t("Usage")}</Title>
                <p>{dag.description}</p>
              </div>
              <div className="mt-5">
                <Title level={5}>{t("Parameters")}</Title>
                <p>Parameter 1 : value 1</p>
                <p>Parameter 2 : value 2</p>
              </div>
            </Tabs.Tab>
            <Tabs.Tab className="mt-4 " label={t("Runs")}>
              <DataGrid
                className="bg-white shadow-md"
                data={dag.runs}
                defaultPageSize={5}
                sortable
                totalItems={dag.runs.length}
                fixedLayout={false}
              >
                <TextColumn
                  className="max-w-[50ch] py-3 "
                  textClassName="font-medium text-gray-600"
                  accessor="id"
                  id="id"
                  label="Id"
                />
                <BaseColumn className="py-3" id="status" label="Status">
                  {(item) => (
                    <PipelineDataCardStatus
                      status={item.status}
                      date={item.executionDate}
                    />
                  )}
                </BaseColumn>
                <TextColumn
                  className="py-3"
                  accessor={(value) => (
                    <>
                      <span>{capitalize(value.triggerMode)}</span>
                    </>
                  )}
                  id="updatedAt"
                  label="Trigger mode"
                />
              </DataGrid>
            </Tabs.Tab>
            <Tabs.Tab className="mt-4" label={t("Settings")}>
              <div>
                <Title level={5}>{t("Api Endpoint")}</Title>
                <p>You can trigger this pipeline with a simple HTTP POST : </p>
                <div className="mt-5 w-2/3">
                  <div className="bg-slate-100 ">
                    <p>{dag.config}</p>
                  </div>
                </div>
              </div>
              <div className="mt-5">
                <Title level={6}> {t("Schedule")} </Title>
                <Input
                  type="text"
                  className="w-1/4"
                  placeholder="23 0-20/2 * * *"
                />
              </div>
            </Tabs.Tab>
          </Tabs>
        </Block>
      </WorkspaceLayout.PageContent>
    </Page>
  );
};

WorkspacePipelinePage.getLayout = (page, pageProps) => {
  return <WorkspaceLayout pageProps={pageProps}>{page}</WorkspaceLayout>;
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
});

export default WorkspacePipelinePage;
