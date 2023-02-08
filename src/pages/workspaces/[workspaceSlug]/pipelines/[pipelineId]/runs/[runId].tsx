import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import DataCard from "core/components/DataCard";
import DateProperty from "core/components/DataCard/DateProperty";
import RenderProperty from "core/components/DataCard/RenderProperty";
import TextProperty from "core/components/DataCard/TextProperty";
import UserProperty from "core/components/DataCard/UserProperty";
import DescriptionList from "core/components/DescriptionList";
import Link from "core/components/Link";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { formatDuration } from "core/helpers/time";
import { NextPageWithLayout } from "core/helpers/types";
import { DagRunStatus, DagRunTrigger } from "graphql-types";
import { DateTime } from "luxon";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import GenericForm from "pipelines/features/PipelineRunForm/GenericForm";
import PipelineRunStatusBadge from "pipelines/features/PipelineRunStatusBadge";
import RunLogs from "pipelines/features/RunLogs";
import RunMessages from "pipelines/features/RunMessages";
import { getPipelineRunLabel } from "pipelines/helpers/runs";
import {
  useWorkspacePipelineRunPageQuery,
  WorkspacePipelineRunPageDocument,
} from "workspaces/graphql/queries.generated";
import { FAKE_WORKSPACE } from "workspaces/helpers/fixtures";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  page: number;
  perPage: number;
};

const WorkspacePipelineRunDetailsPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const router = useRouter();
  const { data } = useWorkspacePipelineRunPageQuery({
    variables: { workspaceSlug: router.query.workspaceSlug as string },
  });

  if (!data?.workspace) {
    return null;
  }
  const { workspace } = data;

  const dag = FAKE_WORKSPACE.dags.find((d) => d.id === router.query.pipelineId);

  if (!dag) {
    return null;
  }

  const dagRun = dag.runs.find((r) => r.id === router.query.runId);

  if (!dagRun) {
    return null;
  }

  const isFinished = [DagRunStatus.Failed, DagRunStatus.Success].includes(
    dagRun.status
  );

  return (
    <Page title={t("Workspace")}>
      <WorkspaceLayout.Header>
        <Breadcrumbs withHome={false}>
          <Breadcrumbs.Part
            isFirst
            href={`/workspaces/${encodeURIComponent(workspace.slug)}`}
          >
            {workspace.name}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part
            href={`/workspaces/${encodeURIComponent(
              workspace.slug
            )}/pipelines}`}
          >
            {t("Pipelines")}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part
            href={`/workspaces/${encodeURIComponent(
              workspace.slug
            )}/pipelines/${encodeURIComponent(dag.id)}`}
          >
            {dag.label}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part
            isLast
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
        <Block className="divide-y-2 divide-gray-100">
          <Block.Header>
            <div className="flex items-center justify-between">
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center">
                  <div className="w-full truncate">
                    <div className="truncate text-sm font-medium text-gray-900">
                      {getPipelineRunLabel(dagRun, dag)}
                    </div>
                    <div className="mt-1.5 text-sm font-normal text-gray-500">
                      {dagRun.status === DagRunStatus.Success &&
                        t("succeeded {{relativeTime}} on ", {
                          relativeTime: DateTime.fromISO(
                            dagRun.executionDate
                          ).toLocaleString(DateTime.DATETIME_SHORT),
                        })}
                      {dagRun.status === DagRunStatus.Failed &&
                        t("failed {{relativeTime}} on", {
                          relativeTime: DateTime.fromISO(
                            dagRun.executionDate
                          ).toLocaleString(DateTime.DATETIME_SHORT),
                        })}
                      {dagRun.status === DagRunStatus.Queued &&
                        t("queued {{relativeTime}}", {
                          relativeTime: DateTime.fromISO(
                            dagRun.executionDate
                          ).toLocaleString(DateTime.DATETIME_SHORT),
                        })}
                      {dagRun.status === DagRunStatus.Running &&
                        t("started {{relativeTime}}", {
                          relativeTime: DateTime.fromISO(
                            dagRun.executionDate
                          ).toLocaleString(DateTime.DATETIME_SHORT),
                        })}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div
                    title={dagRun.executionDate}
                    suppressHydrationWarning={true}
                  >
                    <PipelineRunStatusBadge dagRun={dagRun} />
                  </div>
                </div>
              </div>
            </div>
          </Block.Header>
          <Block.Section title={"Output"}>
            {isFinished && (
              <DescriptionList>
                {dagRun.outputs.map((file, index) => (
                  <DescriptionList.Item key={index} label={file.title}>
                    <Link href={file.uri}>{file.uri}</Link>
                  </DescriptionList.Item>
                ))}
              </DescriptionList>
            )}
          </Block.Section>
          <Block.Section title={t("Messages")}>
            <RunMessages dagRun={dagRun} />
          </Block.Section>
          <Block.Section title={t("Configuration")}>
            <GenericForm fromConfig={dagRun.config} readOnly />
          </Block.Section>
          <Block.Section title={t("Logs")} collapsible>
            <RunLogs dagRun={dagRun} />
          </Block.Section>

          <DataCard item={dagRun}>
            <DataCard.FormSection title={t("Metadata")} defaultOpen={false}>
              <TextProperty
                required
                id="externalId"
                accessor="externalId"
                label={t("Identifier")}
                defaultValue="-"
              />
              <RenderProperty id="dag" label={t("DAG")}>
                {() => (
                  <Link
                    href={{
                      pathname: "/pipelines/[pipelineId]",
                      query: { pipelineId: dag.id },
                    }}
                  >
                    {dag.label || dag.externalId}
                  </Link>
                )}
              </RenderProperty>
              <DateProperty
                id="executionDate"
                accessor="executionDate"
                label={t("Execution Date")}
              />
              <UserProperty id="user" accessor="user" label={t("User")} />
              <RenderProperty readonly id="triggerMode" label={t("Trigger")}>
                {(property) =>
                  property.displayValue.triggerMode === DagRunTrigger.Manual ? (
                    <span>{t("Manual")}</span>
                  ) : (
                    <span>{t("Scheduled")}</span>
                  )
                }
              </RenderProperty>
              <RenderProperty
                readonly
                id="duration"
                accessor="duration"
                label={t("Duration")}
              >
                {(property) => (
                  <span>
                    {property.displayValue
                      ? formatDuration(property.displayValue)
                      : "-"}
                  </span>
                )}
              </RenderProperty>
            </DataCard.FormSection>
          </DataCard>
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
  async getServerSideProps(ctx, client) {
    const { data } = await client.query({
      query: WorkspacePipelineRunPageDocument,
      variables: { id: ctx.params?.workspaceId },
    });

    if (!data.workspace) {
      return {
        notFound: true,
      };
    }
  },
});

export default WorkspacePipelineRunDetailsPage;
