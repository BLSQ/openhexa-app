import { gql } from "@apollo/client";
import { ExternalLinkIcon, PlayIcon } from "@heroicons/react/outline";
import Button from "core/components/Button";
import DataCard from "core/components/DataCard";
import DateProperty from "core/components/DataCard/DateProperty";
import RenderProperty from "core/components/DataCard/RenderProperty";
import TextProperty from "core/components/DataCard/TextProperty";
import UserProperty from "core/components/DataCard/UserProperty";
import Link from "core/components/Link";
import ProgressPie from "core/components/ProgressPie";
import Spinner from "core/components/Spinner";
import { formatDuration } from "core/helpers/time";
import useInterval from "core/hooks/useInterval";
import useRelativeTime from "core/hooks/useRelativeTime";
import { DagRunStatus, DagRunTrigger } from "graphql-types";
import { useTranslation } from "next-i18next";
import { useCallback, useMemo } from "react";
import PipelineRunReadonlyForm from "../PipelineRunForm/PipelineRunReadonlyForm";
import PipelineRunOutputEntry from "../PipelineRunOutputEntry";
import PipelineRunStatusBadge from "../PipelineRunStatusBadge";
import RunLogs from "../RunLogs";
import RunMessages from "../RunMessages";
import {
  PipelineRunDataCard_DagFragment,
  PipelineRunDataCard_DagRunFragment,
} from "./PipelineRunDataCard.generated";

type PipelineRunDataCardProps = {
  onRefresh(): void;
  dag: PipelineRunDataCard_DagFragment;
  dagRun: PipelineRunDataCard_DagRunFragment;
};

const PipelineRunDataCard = (props: PipelineRunDataCardProps) => {
  const { onRefresh, dag, dagRun } = props;
  const { t } = useTranslation();

  const intervalDuration = useMemo(() => {
    switch (dagRun?.status) {
      case DagRunStatus.Queued:
        return 10 * 1000;
      case DagRunStatus.Running:
        return 3 * 1000;
      default:
        return null;
    }
  }, [dagRun]);

  useInterval(
    useCallback(() => {
      onRefresh();
    }, [onRefresh]),
    intervalDuration
  );

  const durationStr = useMemo(
    () => (dagRun.duration ? formatDuration(dagRun.duration) : null),
    [dagRun.duration]
  );
  const isFinished = useMemo(
    () => [DagRunStatus.Failed, DagRunStatus.Success].includes(dagRun.status),
    [dagRun.status]
  );

  const executionDateRelative = useRelativeTime(dagRun.executionDate);

  return (
    <DataCard item={dagRun}>
      <DataCard.Heading<typeof dagRun>
        renderActions={(item) => (
          <div className="flex items-center gap-2.5">
            <a href={item.externalUrl} target="_blank" rel="noreferrer">
              <Button
                variant="white"
                size="sm"
                leadingIcon={<ExternalLinkIcon className="w-5" />}
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
              <Button size="sm" leadingIcon={<PlayIcon className="w-5" />}>
                {t("Re-run job")}
              </Button>
            </Link>
          </div>
        )}
      >
        {() => (
          <div className="flex items-center gap-4">
            {!isFinished && (
              <ProgressPie
                background="stroke-sky-100"
                foreground="stroke-sky-500"
                progress={dagRun.progress}
                textClassName="text-sky-600"
                className="h-10 w-10"
              />
            )}
            <div title={dagRun.executionDate}>
              {dagRun.triggerMode === DagRunTrigger.Manual
                ? t("Manual run of {{label}} by {{user}}", {
                    label: dag.label || dag.externalId,
                    user: dagRun.user?.displayName,
                  })
                : t("Scheduled run of {{label}}", {
                    label: dag.label || dag.externalId,
                  })}
              <div className="mt-1.5 text-sm font-normal text-gray-500">
                {dagRun.status === DagRunStatus.Success &&
                  t("succeeded {{relativeTime}} in {{durationStr}}", {
                    durationStr,
                    relativeTime: executionDateRelative,
                  })}
                {dagRun.status === DagRunStatus.Failed &&
                  t("failed {{relativeTime}} in {{durationStr}}", {
                    durationStr,
                    relativeTime: executionDateRelative,
                  })}
                {dagRun.status === DagRunStatus.Queued &&
                  t("queued {{relativeTime}}", {
                    relativeTime: executionDateRelative,
                  })}
                {dagRun.status === DagRunStatus.Running &&
                  t("started {{relativeTime}}", {
                    relativeTime: executionDateRelative,
                  })}
              </div>
            </div>
            <div className="flex items-center">
              <PipelineRunStatusBadge dagRun={dagRun} />
            </div>
          </div>
        )}
      </DataCard.Heading>
      {isFinished && (
        <DataCard.Section>
          <RenderProperty<{ title: string; uri: string }[]>
            readonly
            id="outputs"
            accessor="outputs"
            label={t("Outputs")}
          >
            {(property) => (
              <>
                {property.displayValue.length === 0 && "-"}
                {property.displayValue.length > 0 &&
                  property.displayValue.map((output, i) => (
                    <span key={i}>
                      <PipelineRunOutputEntry output={output} />
                      {i < property.displayValue.length - 1 && <span>, </span>}
                    </span>
                  ))}
              </>
            )}
          </RenderProperty>
        </DataCard.Section>
      )}
      <DataCard.Section
        right={intervalDuration ? <Spinner size="sm" /> : null}
        title={t("Messages")}
        defaultOpen
      >
        {dagRun.messages.length ? <RunMessages dagRun={dagRun} /> : null}
      </DataCard.Section>
      <DataCard.Section title={t("Configuration")} defaultOpen>
        <PipelineRunReadonlyForm dag={dag} dagRun={dagRun} />
      </DataCard.Section>
      {isFinished && (
        <DataCard.Section
          title={t("Logs")}
          defaultOpen={false}
          right={intervalDuration ? <Spinner size="sm" /> : null}
        >
          <RunLogs dagRun={dagRun} />
        </DataCard.Section>
      )}
      <DataCard.Section title={t("Metadata")} defaultOpen={false}>
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
      </DataCard.Section>
    </DataCard>
  );
};

PipelineRunDataCard.fragments = {
  dag: gql`
    fragment PipelineRunDataCard_dag on DAG {
      id
      externalId
      label
      ...PipelineRunReadonlyForm_dag
    }
    ${PipelineRunReadonlyForm.fragments.dag}
  `,
  dagRun: gql`
    fragment PipelineRunDataCard_dagRun on DAGRun {
      id
      externalId
      externalUrl
      executionDate
      triggerMode
      status
      config
      duration
      outputs {
        ...PipelineRunOutputEntry_output
      }
      user {
        displayName
        ...UserProperty_user
      }
      progress
      messages {
        __typename
      }
      ...RunMessages_dagRun
      ...RunLogs_dagRun
      ...PipelineRunStatusBadge_dagRun
      ...PipelineRunReadonlyForm_dagRun
    }
    ${PipelineRunReadonlyForm.fragments.dagRun}
    ${PipelineRunOutputEntry.fragments.output}
    ${UserProperty.fragments.user}
    ${RunMessages.fragments.dagRun}
    ${RunLogs.fragments.dagRun}
    ${PipelineRunStatusBadge.fragments.dagRun}
  `,
};

export default PipelineRunDataCard;
