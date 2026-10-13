import { ArrowPathIcon } from "@heroicons/react/24/outline";
import Block from "core/components/Block";
import Button from "core/components/Button";
import DescriptionList from "core/components/DescriptionList";
import Page from "core/components/Page";
import Switch from "core/components/Switch";
import Time from "core/components/Time";
import { createGetServerSideProps } from "core/helpers/page";
import { formatDuration } from "core/helpers/time";
import { NextPageWithLayout } from "core/helpers/types";
import PublicLayout from "core/layouts/public/PublicLayout";
import { PipelineRunStatus } from "graphql/types";
import { getMe } from "identity/helpers/auth";
import isNil from "lodash/isNil";
import { useTranslation } from "next-i18next";
import Link from "next/link";
import { getPublicPipelinePath } from "pipelines/features/PipelineVisibility";
import PipelineRunStatusBadge from "pipelines/features/PipelineRunStatusBadge";
import RunMessages from "pipelines/features/RunMessages";
import {
  PublicPipelineRunPageDocument,
  PublicPipelineRunPageQuery,
  PublicPipelineRunPageQueryVariables,
  usePublicPipelineRunPageQuery,
} from "pipelines/graphql/queries.generated";
import usePipelineRunMessages from "pipelines/hooks/usePipelineRunMessages/usePipelineRunMessages";

type PublicPipelineRunPageProps = {
  pipelineId: string;
  runId: string;
};

const TERMINAL_STATUSES = [
  PipelineRunStatus.Failed,
  PipelineRunStatus.Success,
  PipelineRunStatus.Stopped,
  PipelineRunStatus.Skipped,
];

// A run launched from a public permalink, as its visitor follows it: status,
// the values they entered and the messages. No outputs or container logs,
// those stay with the workspace.
const PublicPipelineRunPage: NextPageWithLayout = ({
  pipelineId,
  runId,
}: PublicPipelineRunPageProps) => {
  const { t } = useTranslation();
  const { data, refetch } = usePublicPipelineRunPageQuery({
    variables: { id: runId },
    // The member run page polls through a dedicated query; here the page query
    // is small enough to be the poll itself, until the run settles.
    pollInterval: 1000,
    skipPollAttempt: () =>
      TERMINAL_STATUSES.includes(
        data?.publicPipelineRun?.status ?? PipelineRunStatus.Queued,
      ),
  });
  const run = data?.publicPipelineRun;
  const isTerminal = TERMINAL_STATUSES.includes(
    run?.status ?? PipelineRunStatus.Queued,
  );
  const {
    messages: sseMessages,
    isStreaming,
    streamError,
    reload: reloadStream,
  } = usePipelineRunMessages(runId, isTerminal, refetch);

  if (!run) {
    return null;
  }

  const renderValue = (
    parameter: { type: string; multiple: boolean },
    value: any,
  ) => {
    if (parameter.type === "bool") {
      return <Switch checked={Boolean(value)} disabled />;
    }
    if (isNil(value) || value === "") {
      return "-";
    }
    return parameter.multiple ? ensureList(value).join(", ") : String(value);
  };

  return (
    <Page title={run.pipeline.name}>
      <PublicLayout>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">
              {run.pipeline.name}
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              {t("Run started on")} <Time datetime={run.executionDate} />
            </p>
          </div>
          {isTerminal && (
            <Link href={getPublicPipelinePath(pipelineId)}>
              <Button leadingIcon={<ArrowPathIcon className="h-4 w-4" />}>
                {t("Run again")}
              </Button>
            </Link>
          )}
        </div>

        <Block className="divide-y-2 divide-gray-100">
          <Block.Content>
            <DescriptionList>
              <DescriptionList.Item label={t("Status")}>
                <PipelineRunStatusBadge run={run} />
              </DescriptionList.Item>
              {run.status === PipelineRunStatus.Running && (
                <DescriptionList.Item label={t("Progress")}>
                  {run.progress}%
                </DescriptionList.Item>
              )}
              {isTerminal && (
                <DescriptionList.Item label={t("Duration")}>
                  {run.duration ? formatDuration(run.duration) : "-"}
                </DescriptionList.Item>
              )}
            </DescriptionList>
          </Block.Content>
          {run.pipeline.parameters.length > 0 && (
            <Block.Section title={t("Parameters")}>
              <DescriptionList>
                {run.pipeline.parameters.map((parameter) => (
                  <DescriptionList.Item
                    key={parameter.code}
                    label={parameter.name}
                  >
                    {renderValue(parameter, run.config[parameter.code])}
                  </DescriptionList.Item>
                ))}
              </DescriptionList>
            </Block.Section>
          )}
          <Block.Section title={t("Messages")}>
            <RunMessages
              run={run}
              messages={isTerminal ? undefined : sseMessages}
              isStreaming={isTerminal ? undefined : isStreaming}
              streamError={streamError}
              onReload={reloadStream}
            />
          </Block.Section>
        </Block>
      </PublicLayout>
    </Page>
  );
};

const ensureList = (value: any): any[] =>
  Array.isArray(value) ? value : [value];

PublicPipelineRunPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: false,
  async getServerSideProps(ctx, client) {
    const pipelineId = ctx.params!.pipelineId as string;
    const runId = ctx.params!.runId as string;
    const [{ data }, me] = await Promise.all([
      client.query<
        PublicPipelineRunPageQuery,
        PublicPipelineRunPageQueryVariables
      >({
        query: PublicPipelineRunPageDocument,
        variables: { id: runId },
      }),
      getMe(ctx),
    ]);

    const run = data.publicPipelineRun;
    if (run && run.pipeline.id === pipelineId) {
      return { props: { pipelineId, runId } };
    }
    // A member's run, or one of a pipeline taken back: the login may be what
    // is missing for an anonymous visitor; a member has nowhere else to be sent.
    if (!me?.user) {
      return {
        redirect: {
          permanent: false,
          destination: `/login?next=${encodeURIComponent(ctx.resolvedUrl)}`,
        },
      };
    }
    return { notFound: true };
  },
});

export default PublicPipelineRunPage;
