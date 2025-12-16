import { ExclamationTriangleIcon } from "@heroicons/react/24/outline";
import { gql } from "@apollo/client";
import clsx from "clsx";
import Badge from "core/components/Badge";
import Spinner from "core/components/Spinner";
import Tooltip from "core/components/Tooltip";
import { PipelineRunStatus } from "graphql/types";
import { useTranslation } from "next-i18next";
import { formatPipelineRunStatus } from "pipelines/helpers/format";
import usePipelineRunPoller from "pipelines/hooks/usePipelineRunPoller";
import { useMemo } from "react";
import { PipelineRunStatusBadge_RunFragment } from "./PipelineRunStatusBadge.generated";

type PipelineRunStatusBadgeProps = {
  run: any | PipelineRunStatusBadge_RunFragment; // 'any' the time that we remove the legacy pipelines
  polling?: boolean;
};

const PipelineRunStatusBadge = (props: PipelineRunStatusBadgeProps) => {
  const { t } = useTranslation();
  const { run, polling = true } = props;
  usePipelineRunPoller(run, polling);
  let className = useMemo(() => {
    switch (run.status) {
      case PipelineRunStatus.Stopped:
        return "bg-yellow-100 text-gray-600";
      case PipelineRunStatus.Failed:
        return "bg-red-100 text-red-500";
      case PipelineRunStatus.Queued:
        return "bg-gray-100 text-gray-600";
      case PipelineRunStatus.Running:
      case PipelineRunStatus.Terminating:
        return "bg-sky-100 text-sky-600";
      case PipelineRunStatus.Success:
        return "bg-emerald-50 text-emerald-500";
      case PipelineRunStatus.Skipped:
        return "bg-gray-100 text-gray-500";
    }
  }, [run.status]);

  const loading = useMemo(() => {
    return (
      run.status === PipelineRunStatus.Running ||
      run.status === PipelineRunStatus.Terminating
    );
  }, [run.status]);

  const showWarning =
    run.status === PipelineRunStatus.Success && run.hasErrorMessages;

  return (
    <Badge className={clsx(className, "flex items-center ring-gray-500/20")}>
      {loading && <Spinner className="mr-1" size="xs" />}
      {showWarning && (
        <Tooltip
          label={t("This run completed with errors or warnings in the logs")}
          as="span"
        >
          <ExclamationTriangleIcon className="mr-1 h-3.5 w-3.5 text-amber-500" />
        </Tooltip>
      )}
      {formatPipelineRunStatus(run.status)}
    </Badge>
  );
};

PipelineRunStatusBadge.fragments = {
  pipelineRun: gql`
    fragment PipelineRunStatusBadge_run on PipelineRun {
      id
      status
      hasErrorMessages
      ...usePipelineRunPoller_run
    }
    ${usePipelineRunPoller.fragments.run}
  `,
};

export default PipelineRunStatusBadge;

// TODO : refresh
// TODO : design