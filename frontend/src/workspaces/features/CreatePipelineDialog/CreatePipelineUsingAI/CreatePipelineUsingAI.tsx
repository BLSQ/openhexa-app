import { SparklesIcon } from "@heroicons/react/24/outline";
import AiDisabledBanner from "assistant/components/AiDisabledBanner";
import Textarea from "core/components/forms/Textarea/Textarea";
import useMe from "identity/hooks/useMe";
import { useTranslation } from "next-i18next";
import { useEffect, useRef } from "react";
import { AIFormInstance } from "./useAIForm";

const MAX_TEXTAREA_HEIGHT = 480;

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
            {t("Describe your pipeline and the AI will generate the code to get you started.")}
          </p>
        </div>
      </div>
      <div className="mx-auto w-4/5">
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
          />
        </div>
        {form.error && <p className="mt-1 text-sm text-red-500">{form.error}</p>}
      </div>
    </div>
  ) : (
    <AiDisabledBanner />
  );
};

export default CreatePipelineUsingAI;
