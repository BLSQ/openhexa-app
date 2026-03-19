import Textarea from "core/components/forms/Textarea/Textarea";
import { Trans, useTranslation } from "next-i18next";
import { AIFormInstance } from "./useAIForm";

type CreatePipelineUsingAIProps = {
  form: AIFormInstance;
};

const CreatePipelineUsingAI = ({ form }: CreatePipelineUsingAIProps) => {
  const { t } = useTranslation();

  return (
    <div className="space-y-3">
      <p className="text-sm text-gray-600">
        <Trans>
          Describe the pipeline you want to create. The AI will generate a
          pipeline record and a starter Python file for you.
        </Trans>
      </p>
      <Textarea
        value={form.prompt}
        onChange={(e) => form.setPrompt(e.target.value)}
        placeholder={t(
          "e.g. A pipeline that fetches data from DHIS2 and uploads it to a dataset",
        )}
        rows={5}
      />
      {form.error && <p className="text-sm text-red-500">{form.error}</p>}
    </div>
  );
};

export default CreatePipelineUsingAI;
