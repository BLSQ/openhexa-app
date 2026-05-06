import Select from "core/components/forms/Select";
import Spinner from "core/components/Spinner";
import { ensureArray } from "core/helpers/array";
import { useTranslation } from "next-i18next";
import { useGetPipelineParameterChoicesQuery } from "./ChoicesFromFileWidget.generated";

type ChoicesFromFileWidgetProps = {
  parameter: any;
  value: any;
  onChange(value: any): void;
  workspaceSlug: string;
  pipelineVersionId: string;
};

function getInvalidChoices(choices: string[], type: string): string[] {
  if (type === "int") return choices.filter((c) => isNaN(parseInt(c, 10)));
  if (type === "float") return choices.filter((c) => isNaN(parseFloat(c)));
  return [];
}

const ChoicesFromFileWidget = ({
  parameter,
  value,
  onChange,
  workspaceSlug,
  pipelineVersionId,
}: ChoicesFromFileWidgetProps) => {
  const { t } = useTranslation();

  const { data, loading, error } = useGetPipelineParameterChoicesQuery({
    variables: {
      workspaceSlug,
      pipelineVersionId,
      parameterCode: parameter.code,
    },
  });

  if (loading) {
    return (
      <div className="flex h-9 items-center gap-2 text-sm text-gray-500">
        <Spinner size="xs" />
        <span>{t("Loading choices...")}</span>
      </div>
    );
  }

  if (error || !data?.pipelineParameterChoices) {
    return (
      <p className="text-sm text-red-600">
        {t("Could not load choices: {{message}}", {
          message: error?.message ?? t("file not found or unreadable"),
        })}
      </p>
    );
  }

  const choices = data.pipelineParameterChoices;
  const invalidChoices = getInvalidChoices(choices, parameter.type);

  const listed = invalidChoices
    .slice(0, 3)
    .map((v) => `"${v}"`)
    .join(", ");
  const extra = invalidChoices.length - 3;

  return (
    <>
      <Select
        onChange={onChange}
        aria-label={parameter.code}
        name={parameter.code}
        value={parameter.multiple ? ensureArray(value) : value}
        required={Boolean(parameter.required)}
        multiple={parameter.multiple}
        options={choices}
        getOptionLabel={(option) => option}
        by={(a: string, b: string) => a === b}
      />
      {invalidChoices.length > 0 && (
        <p className="mt-1 text-sm text-amber-600">
          {extra > 0
            ? t(
                "{{count}} choices in this file cannot be used as {{type}} values: {{values}} and {{extra}} more.",
                {
                  count: invalidChoices.length,
                  type: parameter.type,
                  values: listed,
                  extra,
                },
              )
            : t(
                "{{count}} choice(s) in this file cannot be used as {{type}} values: {{values}}.",
                {
                  count: invalidChoices.length,
                  type: parameter.type,
                  values: listed,
                },
              )}
        </p>
      )}
    </>
  );
};

export default ChoicesFromFileWidget;
