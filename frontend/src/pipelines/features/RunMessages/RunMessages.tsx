import { gql } from "@apollo/client";
import Badge from "core/components/Badge";
import Link from "core/components/Link";
import Spinner from "core/components/Spinner";
import Time from "core/components/Time";
import useAutoScroll from "core/hooks/useAutoScroll";
import { PipelineRunStatus } from "graphql/types";
import Linkify from "linkify-react";
import { DateTime } from "luxon";
import { useTranslation } from "next-i18next";
import { useRef } from "react";
import { SseMessage } from "pipelines/hooks/usePipelineRunMessages/usePipelineRunMessages";
import {
  RunMessages_DagRunFragment,
  RunMessages_RunFragment,
} from "./RunMessages.generated";

type RunMessagesProps = {
  run: RunMessages_DagRunFragment | RunMessages_RunFragment;
  // When provided, replaces run.messages entirely (used for live SSE streaming)
  messages?: SseMessage[];
  isStreaming?: boolean;
  streamError?: string | null;
};

function getBadgeClassName(priority: string) {
  switch (priority) {
    case "DEBUG":
      return "bg-gray-50 text-gray-500 ring-gray-500/20";
    case "INFO":
      return "bg-sky-100 text-sky-600 ring-sky-500/20";
    case "WARNING":
      return "bg-amber-50 text-amber-600 ring-amber-500/20";
    case "ERROR":
      return "bg-red-100 text-red-500 ring-red-500/20";
    default:
      return undefined;
  }
}

const RunMessages = (props: RunMessagesProps) => {
  const { t } = useTranslation();
  const { run, messages: messagesOverride, isStreaming, streamError } = props;
  const ref = useRef<HTMLDivElement>(null);
  useAutoScroll(ref, "smooth");

  const messages = messagesOverride !== undefined ? messagesOverride : run.messages;

  const isTerminal = [
    PipelineRunStatus.Failed,
    PipelineRunStatus.Success,
    PipelineRunStatus.Stopped,
    PipelineRunStatus.Skipped,
  ].includes(run.status as PipelineRunStatus);

  const showWaiting =
    isStreaming ?? run.status === PipelineRunStatus.Running;

  return (
    <>
      <div className="max-h-96 overflow-y-auto">
        <div ref={ref}>
          {messages.length === 0 && isTerminal ? (
            <p className="text-sm italic text-gray-600">{t("No messages")}</p>
          ) : (
            <table className="table-fixed">
              <tbody>
                {messages.map((message, index) => (
                  <tr key={index}>
                    <td className="p-1">
                      <Badge className={getBadgeClassName(message.priority)}>
                        {message.priority}
                      </Badge>
                    </td>
                    <td className="p-1">
                      <Time
                        className="text-sm text-gray-400"
                        datetime={message.timestamp}
                        format={DateTime.DATETIME_SHORT_WITH_SECONDS}
                      />
                    </td>
                    <td className="p-1 text-sm">
                      <Linkify
                        as="span"
                        options={{
                          render: ({
                            attributes,
                            content,
                          }: {
                            attributes: any;
                            content: any;
                          }) => <Link {...attributes}>{content}</Link>,
                        }}
                      >
                        {message.message}
                      </Linkify>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
      {showWaiting && (
        <div className="flex items-center gap-1.5 text-gray-400 text-sm px-2 py-2">
          <Spinner size="xs" />
          {t("Waiting for messages...")}
        </div>
      )}
      {streamError && (
        <div className="text-sm text-amber-600 px-2 py-2">
          {streamError === "timeout"
            ? t("Live updates timed out. Refresh the page to reconnect.")
            : t("Live updates disconnected. Refresh the page to reconnect.")}
        </div>
      )}
    </>
  );
};

RunMessages.fragments = {
  dagRun: gql`
    fragment RunMessages_dagRun on DAGRun {
      id
      status
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
      status
      messages {
        message
        timestamp
        priority
      }
    }
  `,
};

export default RunMessages;
