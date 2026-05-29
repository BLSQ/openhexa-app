import { CheckIcon, ExclamationTriangleIcon } from "@heroicons/react/24/outline";
import Spinner from "core/components/Spinner";
import { formatToolName, getToolLabels } from "assistant/helpers/toolNames";
import { useTranslation } from "next-i18next";

type Props = {
  toolName: string;
  status: "pending" | "done";
  success?: boolean;
};

export default function ToolCallCard({ toolName, status, success }: Props) {
  const { t } = useTranslation();
  const label = formatToolName(toolName, getToolLabels(t));
  const isError = status === "done" && success === false;

  return (
    <div className="flex justify-start pl-1">
      <div
        className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs ${
          isError
            ? "bg-red-50 border-red-200 text-red-600"
            : "bg-gray-50 border-gray-200 text-gray-500"
        }`}
      >
        {status === "pending" ? (
          <Spinner size="xs" className="text-gray-400 shrink-0" />
        ) : isError ? (
          <ExclamationTriangleIcon className="h-3.5 w-3.5 text-red-500 shrink-0" />
        ) : (
          <CheckIcon className="h-3.5 w-3.5 text-gray-400 shrink-0" />
        )}
        <span className={status === "pending" ? "italic" : ""}>
          {status === "pending"
            ? `${label}…`
            : isError
              ? `${label} – ${t("Failed").toLowerCase()}`
              : label}
        </span>
      </div>
    </div>
  );
}
