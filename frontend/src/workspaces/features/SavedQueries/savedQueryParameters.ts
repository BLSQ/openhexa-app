// Shape of a single declared parameter in a saved query's `parameters` spec.
// Mirrors the backend spec validated in hexa/data_studio/execution.py. The
// backend stores this as a JSON scalar, so these helpers give the frontend a
// typed view over that untyped payload.

export type SavedQueryParameterType =
  | "string"
  | "integer"
  | "number"
  | "boolean"
  | "date";

export type SavedQueryParameterKind = "value" | "enum" | "identifier";

export type SavedQueryParameter = {
  name: string;
  type: SavedQueryParameterType;
  kind: SavedQueryParameterKind;
  required?: boolean;
  default?: string | null;
  choices?: string[];
  min?: number | null;
  max?: number | null;
};

export const PARAMETER_TYPES: SavedQueryParameterType[] = [
  "string",
  "integer",
  "number",
  "boolean",
  "date",
];

export const PARAMETER_KINDS: SavedQueryParameterKind[] = [
  "value",
  "enum",
  "identifier",
];

export const NUMERIC_TYPES: SavedQueryParameterType[] = ["integer", "number"];

export const isNumericType = (type: SavedQueryParameterType): boolean =>
  NUMERIC_TYPES.includes(type);

export const needsChoices = (kind: SavedQueryParameterKind): boolean =>
  kind === "enum" || kind === "identifier";

export const emptyParameter = (): SavedQueryParameter => ({
  name: "",
  type: "string",
  kind: "value",
  required: false,
});

// The backend field is a JSON scalar (typed `any`), so coerce defensively.
export const parseParameters = (raw: unknown): SavedQueryParameter[] => {
  if (!Array.isArray(raw)) {
    return [];
  }
  return raw as SavedQueryParameter[];
};

// Drop fields that don't apply to the chosen type/kind so the persisted spec
// stays clean (e.g. no `choices` on a plain value param, no `min` on a string).
export const cleanParameter = (
  parameter: SavedQueryParameter,
): SavedQueryParameter => {
  const cleaned: SavedQueryParameter = {
    name: parameter.name.trim(),
    type: parameter.type,
    kind: parameter.kind,
  };
  if (parameter.required) {
    cleaned.required = true;
  }
  if (parameter.default !== undefined && parameter.default !== null) {
    const value = String(parameter.default).trim();
    if (value) {
      cleaned.default = value;
    }
  }
  if (needsChoices(parameter.kind)) {
    cleaned.choices = (parameter.choices ?? [])
      .map((choice) => choice.trim())
      .filter(Boolean);
  }
  if (isNumericType(parameter.type)) {
    if (parameter.min !== undefined && parameter.min !== null) {
      cleaned.min = parameter.min;
    }
    if (parameter.max !== undefined && parameter.max !== null) {
      cleaned.max = parameter.max;
    }
  }
  return cleaned;
};

export const cleanParameters = (
  parameters: SavedQueryParameter[],
): SavedQueryParameter[] => parameters.map(cleanParameter);
