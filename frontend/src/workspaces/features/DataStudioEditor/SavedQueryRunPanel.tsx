import { PlayIcon } from "@heroicons/react/24/solid";
import Input from "core/components/forms/Input";
import SimpleSelect from "core/components/forms/SimpleSelect";
import { useTranslation } from "next-i18next";
import { useState } from "react";
import { SavedQueryParameter } from "workspaces/features/SavedQueries/savedQueryParameters";

type Props = {
  parameters: SavedQueryParameter[];
  loading: boolean;
  onRun: (values: Record<string, unknown>) => void;
};

// Only non-empty inputs are sent, so omitted optional parameters fall back to
// their declared defaults on the backend.
const buildValues = (
  parameters: SavedQueryParameter[],
  raw: Record<string, string>,
): Record<string, unknown> => {
  const values: Record<string, unknown> = {};
  for (const parameter of parameters) {
    const value = raw[parameter.name];
    if (value !== undefined && value !== "") {
      values[parameter.name] = value;
    }
  }
  return values;
};

// Renders one input per declared parameter and runs the *saved* version of the
// query by slug (unsaved edits in the SQL editor are not used — save first to
// test them). Results render in the shared results area below.
const SavedQueryRunPanel = ({ parameters, loading, onRun }: Props) => {
  const { t } = useTranslation();
  const [values, setValues] = useState<Record<string, string>>({});

  const setValue = (name: string, value: string) =>
    setValues((current) => ({ ...current, [name]: value }));

  const renderInput = (parameter: SavedQueryParameter) => {
    const value = values[parameter.name] ?? "";
    const onChange = (v: string) => setValue(parameter.name, v);

    if (parameter.choices?.length) {
      return (
        <SimpleSelect
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="h-8 py-0 text-xs"
        >
          <option value="">{parameter.required ? "" : "—"}</option>
          {parameter.choices.map((choice) => (
            <option key={choice} value={choice}>
              {choice}
            </option>
          ))}
        </SimpleSelect>
      );
    }

    if (parameter.type === "boolean") {
      return (
        <SimpleSelect
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="h-8 py-0 text-xs"
        >
          <option value="">—</option>
          <option value="true">true</option>
          <option value="false">false</option>
        </SimpleSelect>
      );
    }

    return (
      <Input
        name={`run-param-${parameter.name}`}
        type={
          parameter.type === "date"
            ? "date"
            : parameter.type === "integer" || parameter.type === "number"
              ? "number"
              : "text"
        }
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={parameter.required ? t("required") : t("optional")}
        className="h-8 text-xs"
        fullWidth
      />
    );
  };

  return (
    <div className="flex shrink-0 flex-wrap items-end gap-3 border-b border-gray-200 bg-gray-50/60 px-3 py-2">
      {parameters.map((parameter) => (
        <label key={parameter.name} className="flex flex-col gap-1">
          <span className="text-xs font-medium text-gray-600">
            {parameter.name}
            {parameter.required && <span className="text-red-500"> *</span>}
            <span className="ml-1 font-normal text-gray-400">
              {parameter.type}
            </span>
          </span>
          <div className="w-44">{renderInput(parameter)}</div>
        </label>
      ))}
      <button
        type="button"
        onClick={() => onRun(buildValues(parameters, values))}
        disabled={loading}
        title={t("Run the saved query with these parameters")}
        className="inline-flex h-8 items-center justify-center gap-1.5 rounded-md bg-blue-600 px-3 text-xs font-medium text-white shadow-xs transition-colors hover:bg-blue-700 disabled:opacity-60"
      >
        <PlayIcon className="h-3 w-3" />
        {loading ? t("Running…") : t("Run with parameters")}
      </button>
    </div>
  );
};

export default SavedQueryRunPanel;
