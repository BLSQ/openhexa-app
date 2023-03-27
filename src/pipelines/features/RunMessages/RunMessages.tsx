import { gql } from "@apollo/client";
import Badge from "core/components/Badge";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import { DateTime } from "luxon";
import { useTranslation } from "next-i18next";
import {
  RunMessages_DagRunFragment,
  RunMessages_RunFragment,
} from "./RunMessages.generated";

type RunMessagesProps = {
  run: RunMessages_DagRunFragment | RunMessages_RunFragment;
};

function getBadgeClassName(priority: string) {
  switch (priority) {
    case "INFO":
      return "bg-sky-100 text-sky-600";
    case "WARNING":
      return "bg-amber-50 text-amber-600";
    case "ERROR":
      return "bg-red-100 text-red-500";
    default:
      return undefined;
  }
}

const RunMessages = (props: RunMessagesProps) => {
  const { t } = useTranslation();
  const { run } = props;

  if (run.messages.length === 0) {
    return <p className="text-sm italic text-gray-600">{t("No messages")}</p>;
  }

  return (
    <DataGrid
      data={run.messages}
      sortable
      totalItems={run.messages.length}
      className="overflow-hidden rounded-md border"
    >
      <DateColumn
        accessor="timestamp"
        label={t("Timestamp")}
        format={DateTime.DATETIME_SHORT_WITH_SECONDS}
        defaultValue="-"
      />
      <BaseColumn accessor="priority" label={t("Priority")}>
        {(value) => <Badge className={getBadgeClassName(value)}>{value}</Badge>}
      </BaseColumn>
      <TextColumn width={400} accessor="message" label={t("Message")} />
    </DataGrid>
  );
};

RunMessages.fragments = {
  dagRun: gql`
    fragment RunMessages_dagRun on DAGRun {
      id
      messages {
        message
        timestamp
        priority
      }
    }
  `,
  run: gql`
    fragment RunMessages_run on PipelineRun {
      id
      messages {
        message
        timestamp
        priority
      }
    }
  `,
};

export default RunMessages;
