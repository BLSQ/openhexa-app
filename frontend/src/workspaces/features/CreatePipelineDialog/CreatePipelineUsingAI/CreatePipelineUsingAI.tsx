import { ArrowPathIcon, CheckCircleIcon, XCircleIcon } from "@heroicons/react/24/solid";
import { ChevronDownIcon, SparklesIcon } from "@heroicons/react/24/outline";
import AiDisabledBanner from "assistant/components/AiDisabledBanner";
import Spinner from "core/components/Spinner";
import Textarea from "core/components/forms/Textarea/Textarea";
import useMe from "identity/hooks/useMe";
import { useTranslation } from "next-i18next";
import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { AIFormInstance, AIPhase } from "./useAIForm";

const MAX_TEXTAREA_HEIGHT = 480;

enum StepStatus {
  Pending = "pending",
  Active = "active",
  Done = "done",
  Error = "error",
}

type StepProps = {
  label: string;
  status: StepStatus;
};

function Step({ label, status }: StepProps) {
  return (
    <div className="flex items-center gap-3">
      <span className="flex h-5 w-5 shrink-0 items-center justify-center">
        {status === StepStatus.Done && (
          <CheckCircleIcon className="h-5 w-5 text-green-500" />
        )}
        {status === StepStatus.Error && (
          <XCircleIcon className="h-5 w-5 text-red-500" />
        )}
        {status === StepStatus.Active && <Spinner size="xs" className="text-blue-500" />}
        {status === StepStatus.Pending && (
          <span className="h-2 w-2 rounded-full bg-gray-300" />
        )}
      </span>
      <span
        className={
          status === StepStatus.Pending
            ? "text-sm text-gray-400"
            : status === StepStatus.Error
              ? "text-sm text-red-600"
              : "text-sm text-gray-700"
        }
      >
        {label}
      </span>
    </div>
  );
}

type CreatePipelineUsingAIProps = {
  form: AIFormInstance;
};

const CreatePipelineUsingAI = ({ form }: CreatePipelineUsingAIProps) => {
  const { t } = useTranslation();
  const aiEnabled = useMe()?.user?.aiSettings?.enabled ?? false;
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, MAX_TEXTAREA_HEIGHT)}px`;
  }, [form.prompt]);

  const [showAgentResponse, setShowAgentResponse] = useState(false);

  useEffect(() => {
    setShowAgentResponse(false);
  }, [form.agentResponse]);

  const { phase, errorAtPhase } = form;
  const isActive = phase !== AIPhase.Idle;
  const isStreaming =
    phase === AIPhase.Generating || phase === AIPhase.CreatingPipeline;

  const generatingStatus = (): StepStatus => {
    if (
      phase === AIPhase.CreatingPipeline ||
      phase === AIPhase.Done
    )
      return StepStatus.Done;
    if (phase === AIPhase.Error) {
      return errorAtPhase === AIPhase.CreatingPipeline ? StepStatus.Done : StepStatus.Error;
    }
    if (phase === AIPhase.Generating) return StepStatus.Active;
    return StepStatus.Pending;
  };

  const creatingStatus = (): StepStatus => {
    if (phase === AIPhase.Done) return StepStatus.Done;
    if (phase === AIPhase.Error && errorAtPhase === AIPhase.CreatingPipeline)
      return StepStatus.Error;
    if (phase === AIPhase.CreatingPipeline) return StepStatus.Active;
    return StepStatus.Pending;
  };

  const openingStatus = (): StepStatus => {
    if (phase === AIPhase.Done) return StepStatus.Active;
    return StepStatus.Pending;
  };

  return aiEnabled ? (
    <div className="space-y-5">
      <div className="flex flex-col items-center gap-4 py-4 text-center">
        <div className="rounded-xl bg-blue-50 p-4">
          <SparklesIcon className="h-6 w-6 text-blue-500" />
        </div>
        <div>
          <h3 className="text-xl font-semibold text-gray-900">
            {t("What do you want to build?")}
          </h3>
          <p className="mt-1.5 text-sm text-gray-500">
            {t(
              "Describe your pipeline and the AI will generate the code to get you started.",
            )}
          </p>
        </div>
      </div>
      <div className="mx-auto w-4/5 space-y-4">
        <div className="overflow-hidden rounded-xl border border-gray-300 focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500">
          <Textarea
            ref={textareaRef}
            value={form.prompt}
            onChange={(e) => form.setPrompt(e.target.value)}
            placeholder={t(
              "e.g. Create a pipeline that fetches data from the DHIS2 API, transform it, and save it as a CSV in the workspace",
            )}
            className="resize-none rounded-none border-0 focus:ring-0"
            autoFocus
            rows={6}
            disabled={isStreaming}
          />
        </div>

        {isActive && (
          <div className="rounded-xl border border-gray-200 bg-gray-50 p-4 space-y-3">
            <Step
              label={t("Generating pipeline code")}
              status={generatingStatus()}
            />
            <Step
              label={t("Creating pipeline")}
              status={creatingStatus()}
            />
            <Step
              label={t("Opening pipeline editor")}
              status={openingStatus()}
            />

            {phase === AIPhase.Error ? (
              <div className="mt-2 space-y-2">
                <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                  {form.error}
                </div>
                {form.agentResponse && (
                  <div>
                    <button
                      onClick={() => setShowAgentResponse((v) => !v)}
                      className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700"
                    >
                      <ChevronDownIcon
                        className={`h-3.5 w-3.5 transition-transform duration-200 ${showAgentResponse ? "rotate-180" : ""}`}
                      />
                      {t("AI feedback")}
                    </button>
                    {showAgentResponse && (
                      <div className="mt-2 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-600">
                        <div className="prose prose-sm prose-gray max-w-none">
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {form.agentResponse}
                          </ReactMarkdown>
                        </div>
                      </div>
                    )}
                  </div>
                )}
                <button
                  onClick={form.handleSubmit}
                  className="flex items-center gap-1.5 rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 shadow-sm hover:bg-gray-50"
                >
                  <ArrowPathIcon className="h-3.5 w-3.5" />
                  {t("Try again")}
                </button>
              </div>
            ) : (
              <button
                onClick={form.cancel}
                className="mt-1 text-xs text-gray-400 hover:text-gray-600 underline underline-offset-2"
              >
                {t("Cancel")}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  ) : (
    <AiDisabledBanner />
  );
};

export default CreatePipelineUsingAI;
