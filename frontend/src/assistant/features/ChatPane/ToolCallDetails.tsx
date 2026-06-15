import Spinner from "core/components/Spinner";
import { useTranslation } from "next-i18next";
import { resolveToolRenderer } from "./toolRenderers";

type Props = {
  toolName: string;
  toolInput?: unknown;
  toolOutput?: unknown;
  success?: boolean;
  status: "pending" | "done";
};

function isEmpty(value: unknown): boolean {
  if (value == null) return true;
  if (typeof value === "object") return Object.keys(value as object).length === 0;
  return value === "";
}

function Section({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1">
      <div className="text-[0.7rem] font-medium uppercase tracking-wide text-gray-400">
        {label}
      </div>
      {children}
    </div>
  );
}

export default function ToolCallDetails({
  toolName,
  toolInput,
  toolOutput,
  success = true,
  status,
}: Props) {
  const { t } = useTranslation();
  const render = resolveToolRenderer(toolName);
  const hasInput = !isEmpty(toolInput);
  const hasOutput = toolOutput !== undefined && toolOutput !== null;

  return (
    <div className="mt-1.5 space-y-3 rounded-lg border border-gray-200 bg-gray-50/60 p-3">
      {hasInput && (
        <Section label={t("Input")}>
          {render({ value: toolInput, kind: "input", toolName, success })}
        </Section>
      )}

      <Section label={t("Output")}>
        {status === "pending" ? (
          <div className="flex items-center gap-1.5 text-xs italic text-gray-400">
            <Spinner size="xs" className="text-gray-400" />
            {t("Running…")}
          </div>
        ) : hasOutput ? (
          render({ value: toolOutput, kind: "output", toolName, success })
        ) : (
          <div className="text-xs italic text-gray-400">{t("No output")}</div>
        )}
      </Section>
    </div>
  );
}
