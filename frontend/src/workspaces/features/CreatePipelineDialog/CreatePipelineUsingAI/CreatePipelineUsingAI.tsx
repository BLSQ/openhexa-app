import { SparklesIcon } from "@heroicons/react/24/outline";
import Textarea from "core/components/forms/Textarea/Textarea";
import { Trans, useTranslation } from "next-i18next";
import { AIFormInstance } from "./useAIForm";

type CreatePipelineUsingAIProps = {
  form: AIFormInstance;
};

const CreatePipelineUsingAI = ({ form }: CreatePipelineUsingAIProps) => {
  const { t } = useTranslation();

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
            <Trans>
              Describe your pipeline and the AI will generate the code to get you started.
            </Trans>
          </p>
        </div>
      </div>
      <div className="mx-auto w-3/4">
        <div className="overflow-hidden rounded-md border border-gray-300 focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500">
          <Textarea
            value={form.prompt}
            onChange={(e) => form.setPrompt(e.target.value)}
            placeholder={t(
              "e.g. Create a pipeline that fetches data from the DHIS2 API, transform it, and save it as a CSV in the workspace",
            )}
            className="rounded-none border-0 focus:ring-0"
            autoFocus
            rows={5}
          />
          <div className="border-t border-gray-200 bg-gray-50 px-3 py-2.5">
            <span className="text-xs text-gray-400">
              {t("Enter to send · Shift+Enter for new line")}
            </span>
          </div>
        </div>
        {form.error && <p className="mt-1 text-sm text-red-500">{form.error}</p>}
      </div>
    </div>
  );
};

export default CreatePipelineUsingAI;
