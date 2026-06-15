import {
  CheckIcon,
  ChevronRightIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";
import clsx from "clsx";
import Spinner from "core/components/Spinner";
import { formatToolName, getToolLabels } from "assistant/helpers/toolNames";
import { useTranslation } from "next-i18next";
import { useState } from "react";
import ToolCallDetails from "./ToolCallDetails";

type Props = {
  toolName: string;
  status: "pending" | "done";
  success?: boolean;
  toolInput?: unknown;
  toolOutput?: unknown;
};

export default function ToolCallCard({
  toolName,
  status,
  success,
  toolInput,
  toolOutput,
}: Props) {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const label = formatToolName(toolName, getToolLabels(t));
  const isError = status === "done" && success === false;

  return (
    <div className="flex justify-start pl-1">
      <div className="max-w-2xl">
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
          className={clsx(
            "flex w-full items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs transition-colors",
            isError
              ? "border-red-200 bg-red-50 text-red-600 hover:bg-red-100/70"
              : "border-gray-200 bg-gray-50 text-gray-500 hover:bg-gray-100",
          )}
        >
          <ChevronRightIcon
            className={clsx(
              "h-3.5 w-3.5 shrink-0 transition-transform",
              open && "rotate-90",
            )}
          />
          {status === "pending" ? (
            <Spinner size="xs" className="shrink-0 text-gray-400" />
          ) : isError ? (
            <ExclamationTriangleIcon className="h-3.5 w-3.5 shrink-0 text-red-500" />
          ) : (
            <CheckIcon className="h-3.5 w-3.5 shrink-0 text-gray-400" />
          )}
          <span className={status === "pending" ? "italic" : ""}>
            {status === "pending"
              ? `${label}…`
              : isError
                ? `${label} – ${t("Failed").toLowerCase()}`
                : label}
          </span>
        </button>

        {open && (
          <ToolCallDetails
            toolName={toolName}
            toolInput={toolInput}
            toolOutput={toolOutput}
            success={success}
            status={status}
          />
        )}
      </div>
    </div>
  );
}
