import { gql } from "@apollo/client";
import { useTranslation } from "next-i18next";
import {
  RunLogs_DagRunFragment,
  RunLogs_RunFragment,
} from "./RunLogs.generated";

type RunLogsProps = {
  run: RunLogs_DagRunFragment | RunLogs_RunFragment;
};

const RunLogs = (props: RunLogsProps) => {
  const { t } = useTranslation();
  const { run } = props;

  if (!run.logs) {
    return (
      <div className="w-full text-center text-sm text-gray-500">
        {t("No logs")}
      </div>
    );
  }

  return (
    <code>
      <pre className="max-h-96 overflow-y-auto whitespace-pre-line break-all text-xs">
        {run.logs}
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
  run: gql`
    fragment RunLogs_run on PipelineRun {
      id
      logs
    }
  `,
};

export default RunLogs;
