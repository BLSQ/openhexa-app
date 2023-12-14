import { gql } from "@apollo/client";
import Badge from "core/components/Badge";
import Overflow from "core/components/Overflow";
import Time from "core/components/Time";
import useAutoScroll from "core/hooks/useAutoScroll";
import { PipelineRunStatus } from "graphql-types";
import { DateTime } from "luxon";
import { useTranslation } from "next-i18next";
import { useMemo, useRef } from "react";
import Linkify from "linkify-react";
import {
  RunMessages_DagRunFragment,
  RunMessages_RunFragment,
} from "./RunMessages.generated";
import Link from "core/components/Link";

type RunMessagesProps = {
  run: RunMessages_DagRunFragment | RunMessages_RunFragment;
};

function getBadgeClassName(priority: string) {
  switch (priority) {
    case "DEBUG":
      return "bg-gray-50 text-gray-500";
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

// Approximate height of a single message row
const MESSAGE_HEIGHT = 40;

const RunMessages = (props: RunMessagesProps) => {
  const { t } = useTranslation();
  const { run } = props;
  const ref = useRef<HTMLDivElement>(null);
  useAutoScroll(ref, "smooth");

  const maxHeight = useMemo(() => {
    if (run.status === PipelineRunStatus.Running) {
      return 400;
    }
    return Math.min(400, MESSAGE_HEIGHT * (run.messages.length + 1));
  }, [run.messages.length, run.status]);

  // Scroll to bottom the container when the height changes

  return (
    <Overflow vertical style={{ height: maxHeight }} forwardedRef={ref}>
      {run.messages.length === 0 ? (
        <p className="text-sm italic text-gray-600">{t("No messages")}</p>
      ) : (
        <table className="table-fixed">
          <tbody>
            {run.messages.map((message, index) => (
              <tr key={index}>
                <td className="p-1.5">
                  <Badge className={getBadgeClassName(message.priority)}>
                    {message.priority}
                  </Badge>
                </td>
                <td className="p-1.5">
                  <Time
                    className="text-sm text-gray-400"
                    datetime={message.timestamp}
                    format={DateTime.DATETIME_SHORT_WITH_SECONDS}
                  />
                </td>
                <td className="p-1.5 text-sm">
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
    </Overflow>
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
