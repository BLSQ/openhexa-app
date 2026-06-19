import { ParameterField_ParameterFragment } from "./ParameterField.generated";

type ParameterOverrides = Partial<ParameterField_ParameterFragment> &
  Pick<ParameterField_ParameterFragment, "code" | "name" | "type">;

/**
 * Builds a complete `ParameterField_ParameterFragment` from a few fields,
 * filling sensible defaults for the rest. Keeps test fixtures terse and avoids
 * repeating every parameter field (notably `disables`/`disableWhen`).
 */
export const makeParameter = (
  overrides: ParameterOverrides,
): ParameterField_ParameterFragment => ({
  required: false,
  multiple: false,
  default: null,
  help: null,
  choices: null,
  widget: null,
  connection: null,
  directory: null,
  disables: [],
  disableWhen: true,
  choicesFromFile: null,
  ...overrides,
});
