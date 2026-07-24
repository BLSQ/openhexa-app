import { PlusIcon, TrashIcon } from "@heroicons/react/24/outline";
import Checkbox from "core/components/forms/Checkbox";
import Input from "core/components/forms/Input";
import SimpleSelect from "core/components/forms/SimpleSelect";
import { useTranslation } from "next-i18next";
import {
  PARAMETER_KINDS,
  PARAMETER_TYPES,
  SavedQueryParameter,
  emptyParameter,
  isNumericType,
  needsChoices,
} from "./savedQueryParameters";

type Props = {
  value: SavedQueryParameter[];
  onChange: (parameters: SavedQueryParameter[]) => void;
};

// Authoring UI for a saved query's parameter spec. Each row declares one
// parameter; the fields shown adapt to the chosen type/kind (choices for
// enum/identifier, min/max for numeric). Referenced in the SQL body as {{ name }}.
const SavedQueryParametersEditor = ({ value, onChange }: Props) => {
  const { t } = useTranslation();

  const updateAt = (index: number, patch: Partial<SavedQueryParameter>) => {
    onChange(
      value.map((param, i) => (i === index ? { ...param, ...patch } : param)),
    );
  };

  const removeAt = (index: number) => {
    onChange(value.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-3">
      {value.length === 0 && (
        <p className="text-sm text-gray-500">
          {t("No parameters yet. Add one, then reference it in your SQL as")}{" "}
          <code className="rounded bg-gray-100 px-1 font-mono">
            {"{{ name }}"}
          </code>
          .
        </p>
      )}
      {value.map((param, index) => (
        <div
          key={index}
          className="space-y-2 rounded-md border border-gray-200 p-3"
        >
          <div className="flex items-start gap-2">
            <Input
              name={`param-name-${index}`}
              placeholder={t("name")}
              value={param.name}
              onChange={(e) => updateAt(index, { name: e.target.value })}
              className="flex-1"
              fullWidth
            />
            <SimpleSelect
              value={param.type}
              onChange={(e) =>
                updateAt(index, {
                  type: e.target.value as SavedQueryParameter["type"],
                })
              }
              className="w-32"
            >
              {PARAMETER_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </SimpleSelect>
            <SimpleSelect
              value={param.kind}
              onChange={(e) =>
                updateAt(index, {
                  kind: e.target.value as SavedQueryParameter["kind"],
                })
              }
              className="w-32"
            >
              {PARAMETER_KINDS.map((kind) => (
                <option key={kind} value={kind}>
                  {kind}
                </option>
              ))}
            </SimpleSelect>
            <button
              type="button"
              onClick={() => removeAt(index)}
              title={t("Remove parameter")}
              aria-label={t("Remove parameter")}
              className="mt-1.5 shrink-0 text-gray-400 hover:text-red-600"
            >
              <TrashIcon className="h-5 w-5" />
            </button>
          </div>

          <div className="flex flex-wrap items-center gap-4">
            <Checkbox
              name={`param-required-${index}`}
              label={t("Required")}
              checked={Boolean(param.required)}
              onChange={(e) => updateAt(index, { required: e.target.checked })}
            />
            <Input
              name={`param-default-${index}`}
              placeholder={t("default value")}
              value={param.default ?? ""}
              onChange={(e) => updateAt(index, { default: e.target.value })}
              className="w-40"
            />
            {isNumericType(param.type) && (
              <div className="flex items-center gap-2">
                <Input
                  name={`param-min-${index}`}
                  type="number"
                  placeholder={t("min")}
                  value={param.min ?? ""}
                  onChange={(e) =>
                    updateAt(index, {
                      min:
                        e.target.value === "" ? null : Number(e.target.value),
                    })
                  }
                  className="w-20"
                />
                <Input
                  name={`param-max-${index}`}
                  type="number"
                  placeholder={t("max")}
                  value={param.max ?? ""}
                  onChange={(e) =>
                    updateAt(index, {
                      max:
                        e.target.value === "" ? null : Number(e.target.value),
                    })
                  }
                  className="w-20"
                />
              </div>
            )}
          </div>

          {needsChoices(param.kind) && (
            <Input
              name={`param-choices-${index}`}
              placeholder={t(
                "Allowed values, comma-separated (e.g. ASC, DESC)",
              )}
              value={(param.choices ?? []).join(", ")}
              onChange={(e) =>
                updateAt(index, {
                  choices: e.target.value.split(",").map((c) => c.trim()),
                })
              }
              fullWidth
            />
          )}
        </div>
      ))}

      <button
        type="button"
        onClick={() => onChange([...value, emptyParameter()])}
        className="inline-flex items-center gap-1.5 text-sm font-medium text-blue-600 hover:text-blue-700"
      >
        <PlusIcon className="h-4 w-4" />
        {t("Add parameter")}
      </button>
    </div>
  );
};

export default SavedQueryParametersEditor;
