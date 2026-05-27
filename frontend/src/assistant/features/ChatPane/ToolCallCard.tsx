import { CheckIcon, ExclamationTriangleIcon } from "@heroicons/react/24/outline";
import Spinner from "core/components/Spinner";
import { formatToolName } from "assistant/helpers/toolNames";

type Props = {
  toolName: string;
  status: "pending" | "done";
  success?: boolean;
};

export default function ToolCallCard({ toolName, status, success }: Props) {
  const label = formatToolName(toolName);

  return (
    <div className="flex justify-start pl-1">
      <div className="flex items-center gap-1.5 rounded-lg bg-gray-50 border border-gray-200 px-3 py-1.5 text-xs text-gray-500">
        {status === "pending" ? (
          <Spinner size="xs" className="text-gray-400 shrink-0" />
        ) : success === false ? (
          <ExclamationTriangleIcon className="h-3.5 w-3.5 text-amber-500 shrink-0" />
        ) : (
          <CheckIcon className="h-3.5 w-3.5 text-gray-400 shrink-0" />
        )}
        <span className={status === "pending" ? "italic" : ""}>
          {status === "pending" ? `${label}…` : label}
        </span>
      </div>
    </div>
  );
}
