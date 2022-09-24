import { gql } from "@apollo/client";
import Badge from "core/components/Badge";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import { useTranslation } from "next-i18next";
import { RunMessages_DagRunFragment } from "./RunMessages.generated";

type RunMessagesProps = {
  dagRun: RunMessages_DagRunFragment;
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
  const { dagRun } = props;

  if (dagRun.messages.length === 0) {
    return (
      <div className="w-full p-5 text-center text-sm text-gray-500">
        {t("No messages")}
      </div>
    );
  }

  return (
    <DataGrid
      data={dagRun.messages}
      sortable
      className="overflow-hidden rounded-md border"
    >
      <DateColumn accessor="timestamp" label={t("Timestamp")} />
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
};

export default RunMessages;
