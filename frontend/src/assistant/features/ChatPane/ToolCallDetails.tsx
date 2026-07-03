import Spinner from "core/components/Spinner";
import { useTranslation } from "next-i18next";
import { AssistantToolName } from "graphql/types";
import { getToolConfig } from "assistant/helpers/toolConfig";
import ToolValueSection from "./ToolValueSection";
import { RenderContext } from "./renderers";

type Props = {
  tool: AssistantToolName | null;
  toolName: string;
  toolInput?: unknown;
  toolOutput?: unknown;
  success?: boolean;
  status: "pending" | "done";
};

function isEmpty(value: unknown): boolean {
  if (value == null) return true;
  if (typeof value === "object")
    return Object.keys(value as object).length === 0;
  return value === "";
}

export default function ToolCallDetails({
  tool,
  toolName,
  toolInput,
  toolOutput,
  success = true,
  status,
}: Props) {
  const { t } = useTranslation();
  const config = getToolConfig(tool);
  const hasInput = !isEmpty(toolInput);
  const hasOutput = !isEmpty(toolOutput);

  const baseCtx = { tool, toolName, success, input: toolInput, output: toolOutput };

  return (
    <div className="mt-1.5 space-y-3 rounded-lg border border-gray-200 bg-gray-50/60 p-3">
      {hasInput && (
        <ToolValueSection
          label={config.inputLabel?.(t) ?? t("Input")}
          value={toolInput}
          ctx={{ ...baseCtx, kind: "input" } as RenderContext}
        />
      )}

      {config.hideOutput ? null : status === "pending" ? (
        <div className="space-y-1">
          <div className="text-[0.7rem] font-medium uppercase tracking-wide text-gray-400">
            {t("Output")}
          </div>
          <div className="flex items-center gap-1.5 text-xs italic text-gray-400">
            <Spinner size="xs" className="text-gray-400" />
            {t("Running…")}
          </div>
        </div>
      ) : hasOutput ? (
        <ToolValueSection
          label={t("Output")}
          value={toolOutput}
          ctx={{ ...baseCtx, kind: "output" } as RenderContext}
        />
      ) : (
        <div className="space-y-1">
          <div className="text-[0.7rem] font-medium uppercase tracking-wide text-gray-400">
            {t("Output")}
          </div>
          <div className="text-xs italic text-gray-400">{t("No output")}</div>
        </div>
      )}
    </div>
  );
}
