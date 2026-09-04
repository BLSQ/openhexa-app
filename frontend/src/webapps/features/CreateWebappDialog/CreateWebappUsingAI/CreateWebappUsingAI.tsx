import { SparklesIcon } from "@heroicons/react/24/outline";
import Textarea from "core/components/forms/Textarea/Textarea";
import { useTranslation } from "next-i18next";
import { useEffect, useRef } from "react";

const MAX_TEXTAREA_HEIGHT = 480;

type CreateWebappUsingAIProps = {
  prompt: string;
  onPromptChange: (value: string) => void;
};

const CreateWebappUsingAI = ({
  prompt,
  onPromptChange,
}: CreateWebappUsingAIProps) => {
  const { t } = useTranslation();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, MAX_TEXTAREA_HEIGHT)}px`;
  }, [prompt]);

  return (
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
              "Describe your web app and the AI will generate the code to get you started.",
            )}
          </p>
        </div>
      </div>
      <div className="mx-auto w-4/5">
        <div className="overflow-hidden rounded-xl border border-gray-300 focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500">
          <Textarea
            ref={textareaRef}
            value={prompt}
            onChange={(e) => onPromptChange(e.target.value)}
            placeholder={t(
              "e.g. Create a dashboard that reads the immunization coverage dataset and shows a map and a trend chart per district",
            )}
            className="resize-none rounded-none border-0 focus:ring-0"
            autoFocus
            rows={6}
          />
        </div>
      </div>
      <p className="mt-2 text-center text-xs text-gray-400">
        {t("AI can make mistakes. Always verify important information.")}
      </p>
    </div>
  );
};

export default CreateWebappUsingAI;
