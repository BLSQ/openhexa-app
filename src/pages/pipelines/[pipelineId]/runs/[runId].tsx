import {
  ClockIcon,
  ExternalLinkIcon,
  PlayIcon,
} from "@heroicons/react/outline";
import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import CodeEditor from "core/components/CodeEditor";
import DataCard from "core/components/DataCard";
import DateProperty from "core/components/DataCard/DateProperty";
import RenderProperty from "core/components/DataCard/RenderProperty";
import TextProperty from "core/components/DataCard/TextProperty";
import UserProperty from "core/components/DataCard/UserProperty";
import Page from "core/components/Layout/Page";
import { PageContent } from "core/components/Layout/PageContent";
import Link from "core/components/Link";
import Title from "core/components/Title";
import { createGetServerSideProps } from "core/helpers/page";
import { formatDuration } from "core/helpers/time";
import useInterval from "core/hooks/useInterval";
import { DagRunStatus, DagRunTrigger } from "graphql-types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import PipelineRunStatusBadge from "pipelines/features/PipelineRunStatusBadge";
import RunLogs from "pipelines/features/RunLogs";
import RunMessages from "pipelines/features/RunMessages";
import {
  PipelineRunPageDocument,
  usePipelineRunPageQuery,
} from "pipelines/graphql/queries.generated";
import { useCallback } from "react";

type Props = {
  page: number;
  perPage: number;
};

const PipelineRunPage = (props: Props) => {
  const { t } = useTranslation();
  const router = useRouter();

  const { data, refetch } = usePipelineRunPageQuery({
    variables: {
      pipelineId: router.query.pipelineId as string,
      runId: router.query.runId as string,
    },
  });

  useInterval(
    useCallback(() => {
      refetch();
    }, [refetch]),
    [DagRunStatus.Running, DagRunStatus.Queued].includes(
      data?.dagRun?.status as any
    )
      ? 15 * 1000
      : null
  );

  if (!data || !data.dag || !data.dagRun) {
    return null;
  }

  const { dagRun, dag } = data;

  return (
    <Page title={t("Pipeline Run")}>
      <PageContent>
        <Breadcrumbs className="my-8 px-2">
          <Breadcrumbs.Part href="/pipelines">
            {t("Data Pipelines")}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part
            href={{
              pathname: "/pipelines/[pipelineId]",
              query: { pipelineId: dag.id },
            }}
          >
            {dag.code}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part
            href={{
              pathname: "/pipelines/[pipelineId]/runs/[runId]",
              query: { pipelineId: dag.id, runId: dagRun.id },
            }}
          >
            {dagRun.externalId}
          </Breadcrumbs.Part>
        </Breadcrumbs>
        <div className="space-y-12">
          <DataCard item={dagRun}>
            <DataCard.Heading<typeof dagRun>
              titleAccessor="externalId"
              renderActions={(item) => (
                <div className="flex items-center gap-2">
                  <a href={item.externalUrl} target="_blank" rel="noreferrer">
                    <Button
                      variant="white"
                      size="sm"
                      leadingIcon={<ExternalLinkIcon className="w-6" />}
                    >
                      {t("Open in Airflow")}
                    </Button>
                  </a>
                  <Link
                    href={{
                      pathname: "/pipelines/[pipelineId]/run",
                      query: { pipelineId: dag.id, fromRun: dagRun.id },
                    }}
                  >
                    <Button
                      size="sm"
                      leadingIcon={<PlayIcon className="w-6" />}
                    >
                      {t("Configure & Re-run")}
                    </Button>
                  </Link>
                </div>
              )}
            />
            <DataCard.Section title={t("Run Data")}>
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
                    {dag.code}
                  </Link>
                )}
              </RenderProperty>
              <DateProperty
                id="executionDate"
                accessor="executionDate"
                label={t("Execution Date")}
              />
              <UserProperty id="user" accessor="user" label={t("User")} />
              <RenderProperty readonly id="status" label={t("Status")}>
                {(item) => (
                  <div>
                    <PipelineRunStatusBadge dagRun={item} />
                  </div>
                )}
              </RenderProperty>
              <RenderProperty readonly id="triggerMode" label={t("Trigger")}>
                {(item) =>
                  item.triggerMode === DagRunTrigger.Manual ? (
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
                {(value) => <span>{value ? formatDuration(value) : "-"}</span>}
              </RenderProperty>
              <RenderProperty
                id="config"
                readonly
                accessor="config"
                label={t("Config")}
              >
                {(value) => (
                  <div className="p-2 text-xs">
                    <CodeEditor
                      editable={false}
                      value={JSON.stringify(value)}
                      lang="json"
                    />
                  </div>
                )}
              </RenderProperty>
            </DataCard.Section>
          </DataCard>
          <div>
            <Title level={3}>{t("Messages")}</Title>
            <Block>
              <RunMessages dagRun={dagRun} />
            </Block>
          </div>
          <div>
            <Title level={3}>{t("Logs")}</Title>
            <Block>
              <Block.Content>
                <RunLogs dagRun={dagRun} />
              </Block.Content>
            </Block>
          </div>
        </div>
      </PageContent>
    </Page>
  );
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  getServerSideProps: async (ctx, client) => {
    const { data } = await client.query({
      query: PipelineRunPageDocument,
      variables: {
        pipelineId: ctx.params?.pipelineId as string,
        runId: ctx.params?.runId as string,
      },
    });
    if (!data.dagRun) {
      return {
        notFound: true,
      };
    }
  },
});

export default PipelineRunPage;
