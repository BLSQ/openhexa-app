import DataGrid, { BaseColumn } from "core/components/DataGrid";
import ChevronLinkColumn from "core/components/DataGrid/ChevronLinkColumn";
import UserColumn from "core/components/DataGrid/UserColumn";
import Link from "core/components/Link";
import Spinner from "core/components/Spinner";
import Time from "core/components/Time";
import TruncatedText from "core/components/TruncatedText";
import { formatDuration } from "core/helpers/time";
import {
  PipelineParameter,
  PipelineRunStatus,
  PipelineRunTrigger,
  PipelineType,
} from "graphql/types";
import { useTranslation } from "next-i18next";
import PipelineRunStatusBadge from "pipelines/features/PipelineRunStatusBadge";
import { formatParamValue } from "pipelines/helpers/format";
import usePipelineRunPoller from "pipelines/hooks/usePipelineRunPoller";
import { useState } from "react";
import { useWorkspacePipelineRunsQuery } from "workspaces/graphql/queries.generated";
import { getPipelineRunConfig } from "workspaces/helpers/pipelines";

const MAX_VISIBLE_PARAMS = 3;
const PER_PAGE = 15;

function RunPoller({
  run,
}: {
  run: { id: string; status: PipelineRunStatus };
}) {
  usePipelineRunPoller(run);
  return null;
}

function RunParametersCell({
  run,
}: {
  run: {
    config: any;
    version?: { parameters: Omit<PipelineParameter, "__typename">[] } | null;
  };
}) {
  const { t } = useTranslation();
  const [isExpanded, setIsExpanded] = useState(false);
  const params = getPipelineRunConfig(run);

  if (!params.length) return <span className="text-gray-400">-</span>;

  const shouldShowToggle = params.length > MAX_VISIBLE_PARAMS;
  const visibleParams = isExpanded
    ? params
    : params.slice(0, MAX_VISIBLE_PARAMS);
  const remainingCount = params.length - MAX_VISIBLE_PARAMS;

  return (
    <div className="max-w-md whitespace-normal space-y-0.5 text-xs text-gray-600">
      {visibleParams.map((p) => (
        <div key={p.code} className="flex min-w-0 items-baseline gap-1">
          <TruncatedText
            lines={1}
            tooltip
            className="shrink-0 max-w-[45%] text-gray-400"
          >
            {`${p.name}:`}
          </TruncatedText>
          <TruncatedText lines={3} tooltip className="flex-1">
            {formatParamValue(p)}
          </TruncatedText>
        </div>
      ))}
      {shouldShowToggle && !isExpanded && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            setIsExpanded(true);
          }}
          className="cursor-pointer text-blue-600 hover:text-blue-800 hover:underline"
        >
          {t("+{{remainingCount}} more", { remainingCount })}
        </button>
      )}
      {isExpanded && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            setIsExpanded(false);
          }}
          className="cursor-pointer text-blue-600 hover:text-blue-800 hover:underline"
        >
          {t("Show less")}
        </button>
      )}
    </div>
  );
}

type PipelineRunsProps = {
  workspaceSlug: string;
  pipelineCode: string;
};

const PipelineRuns = ({ workspaceSlug, pipelineCode }: PipelineRunsProps) => {
  const { t } = useTranslation();
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(PER_PAGE);

  const { data, loading } = useWorkspacePipelineRunsQuery({
    variables: { workspaceSlug, pipelineCode, page, perPage },
  });

  const pipeline = data?.pipeline;

  if (!pipeline) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner size="sm" />
      </div>
    );
  }

  const runs = pipeline.runs.items;

  if (!loading && runs.length === 0 && page === 1) {
    return (
      <div className="py-12 text-center text-sm text-gray-500">
        {t("This pipeline has not been run yet.")}
      </div>
    );
  }

  return (
    <>
      {runs.map((run) => (
        <RunPoller key={run.id} run={run} />
      ))}
      <DataGrid
        defaultPageSize={perPage}
        defaultPageIndex={page - 1}
        data={runs}
        totalItems={pipeline.runs.totalItems}
        fixedLayout={false}
        fetchData={({ page: nextPage, pageSize }) => {
          setPage(nextPage);
          setPerPage(pageSize);
        }}
      >
        <BaseColumn id="name" label={t("Executed on")}>
          {(item) => (
            <Link
              customStyle="text-gray-700 font-medium"
              href={{
                pathname:
                  "/workspaces/[workspaceSlug]/pipelines/[pipelineCode]/runs/[runId]",
                query: { pipelineCode, workspaceSlug, runId: item.id },
              }}
            >
              <Time datetime={item.executionDate} />
            </Link>
          )}
        </BaseColumn>
        <BaseColumn<PipelineRunTrigger>
          label={t("Trigger")}
          accessor="triggerMode"
        >
          {(value) => (
            <span>
              {value === PipelineRunTrigger.Scheduled && t("Scheduled")}
              {value === PipelineRunTrigger.Manual && t("Manual")}
              {value === PipelineRunTrigger.Webhook && t("Webhook")}
            </span>
          )}
        </BaseColumn>
        <BaseColumn label={t("Status")} id="status">
          {(item) => <PipelineRunStatusBadge run={item} />}
        </BaseColumn>
        {pipeline.type === PipelineType.ZipFile ? (
          <BaseColumn label={t("Version")} id="version">
            {(item) =>
              item.version ? (
                <span>
                  {item.version.isLatestVersion
                    ? t("Latest")
                    : item.version.versionName}
                </span>
              ) : (
                <span>-</span>
              )
            }
          </BaseColumn>
        ) : null}
        <BaseColumn label={t("Duration")} accessor="duration">
          {(value) => (
            <span suppressHydrationWarning>
              {value ? formatDuration(value) : "-"}
            </span>
          )}
        </BaseColumn>
        <UserColumn label={t("User")} accessor="user" />
        <BaseColumn label={t("Parameters")} id="parameters">
          {(item) => <RunParametersCell run={item} />}
        </BaseColumn>
        <ChevronLinkColumn
          accessor="id"
          url={(value: any) => ({
            pathname:
              "/workspaces/[workspaceSlug]/pipelines/[pipelineCode]/runs/[runId]",
            query: { workspaceSlug, pipelineCode, runId: value },
          })}
        />
      </DataGrid>
    </>
  );
};

export default PipelineRuns;
