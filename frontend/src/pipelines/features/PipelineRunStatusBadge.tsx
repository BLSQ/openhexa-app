import { gql } from "@apollo/client";
import clsx from "clsx";
import Badge from "core/components/Badge";
import Spinner from "core/components/Spinner";
import Tooltip from "core/components/Tooltip";
import { PipelineRunStatus } from "graphql/types";
import { useTranslation } from "next-i18next";
import {
  formatPipelineRunStatus,
  getPipelineRunStatusBadgeClassName,
} from "pipelines/helpers/format";
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
  const className = useMemo(
    () => getPipelineRunStatusBadgeClassName(run.status),
    [run.status],
  );

  const loading = useMemo(() => {
    return (
      run.status === PipelineRunStatus.Running ||
      run.status === PipelineRunStatus.Terminating
    );
  }, [run.status]);

  const showWarning =
    run.status === PipelineRunStatus.Success && run.hasErrorMessages;

  return (
    <div className="flex items-center gap-1">
      <Badge className={clsx(className, "flex items-center ring-gray-500/20")}>
        {loading && <Spinner className="mr-1" size="xs" />}
        {formatPipelineRunStatus(run.status)}
      </Badge>
      {showWarning && (
        <Tooltip
          label={t("This run completed with errors or warnings in the logs")}
          as="span"
          placement="right"
        >
          <span className="relative -top-0.5 text-xs">⚠️</span>
        </Tooltip>
      )}
    </div>
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