import { gql } from "@apollo/client";
import { useTranslation } from "next-i18next";
import { RunLogs_DagRunFragment } from "./RunLogs.generated";

type RunLogsProps = {
  dagRun: RunLogs_DagRunFragment;
};

const RunLogs = (props: RunLogsProps) => {
  const { t } = useTranslation();
  const { dagRun } = props;

  if (!dagRun.logs) {
    return (
      <div className="w-full text-center text-sm text-gray-500">
        {t("No logs")}
      </div>
    );
  }

  return (
    <code className="contents">
      <pre className="max-h-96 overflow-y-auto whitespace-pre-line text-xs">
        {dagRun.logs}
      </pre>
    </code>
  );
};

RunLogs.fragments = {
  dagRun: gql`
    fragment RunLogs_dagRun on DAGRun {
      id
      logs
    }
  `,
};

export default RunLogs;
