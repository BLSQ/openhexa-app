import { gql } from "@apollo/client";
import Switch from "core/components/Switch/Switch";
import Input from "core/components/forms/Input/Input";
import Select from "core/components/forms/Select";
import Textarea from "core/components/forms/Textarea/Textarea";
import { ensureArray } from "core/helpers/array";
import { useCallback } from "react";
import { useTranslation } from "react-i18next";

type ParameterFieldProps = {
  parameter: any;
  value: any;
  onChange(value: any): void;
};

const ParameterField = (props: ParameterFieldProps) => {
  const { t } = useTranslation();
  const { parameter, value, onChange } = props;

  const handleChange = useCallback(
    (value: any) => {
      if (parameter.multiple && (value === null || value === undefined)) {
        return onChange([]);
      } else if (parameter.multiple) {
        onChange(value.split("\n"));
      } else {
        onChange(value);
      }
    },
    [onChange, parameter.multiple],
  );

  if (parameter.type === "bool") {
    return (
      <Switch
        name={parameter.code}
        checked={value ?? false}
        onChange={onChange}
      />
    );
  }
  if (parameter.choices?.length) {
    const choices =
      parameter.type !== "str"
        ? parameter.choices.map((choice: number) => String(choice))
        : parameter.choices;
    return (
      <Select
        onChange={handleChange}
        value={value}
        required={Boolean(parameter.required)}
        multiple={parameter.multiple}
        options={choices ?? []}
        getOptionLabel={(option) => option}
        by={(a, b) => a == b}
        onCreate={
          !parameter.choices
            ? (query) =>
                handleChange(
                  parameter.multiple ? [...(value ?? []), query] : query,
                )
            : undefined
        }
      />
    );
  }
  if (parameter.multiple) {
    return (
      <>
        <Textarea
          aria-label={parameter.code}
          name={parameter.code}
          rows={4}
          required={Boolean(parameter.required)}
          className="w-full"
          value={value ? value.join("\n") : ""}
          onChange={(event) => {
            handleChange(event.target.value);
          }}
          data-testid={`${parameter.code}-textarea`}
        ></Textarea>
        <small className="ml-2 text-gray-600">
          {t("Separate values with a new line")}
        </small>
      </>
    );
  }

  switch (parameter.type) {
    case "int":
    case "float":
      return (
        <Input
          type="number"
          name={parameter.code}
          required={Boolean(parameter.required)}
          onChange={(event) => handleChange(event.target.value)}
          value={value ?? ""}
          data-testid={`${parameter.code}-input`}
        />
      );
    case "str":
      return (
        <Input
          type="text"
          aria-label={parameter.code}
          name={parameter.code}
          required={Boolean(parameter.required)}
          onChange={(event) => handleChange(event.target.value)}
          value={value ?? ""}
          data-testid={`${parameter.code}-input`}
        />
      );
  }
  return null;
};

ParameterField.fragments = {
  parameter: gql`
    fragment ParameterField_parameter on PipelineParameter {
      code
      name
      help
      type
      default
      required
      choices
      multiple
    }
  `,
};

export default ParameterField;
