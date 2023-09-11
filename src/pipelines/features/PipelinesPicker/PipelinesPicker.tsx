import { gql, useQuery } from "@apollo/client";
import { Combobox } from "core/components/forms/Combobox";
import { ensureArray } from "core/helpers/array";
import useDebounce from "core/hooks/useDebounce";
import { useTranslation } from "next-i18next";
import { useCallback, useMemo, useState } from "react";
import {
  PipelinesPickerQuery,
  PipelinesPickerQueryVariables,
  PipelinesPicker_ValueFragment,
} from "./PipelinesPicker.generated";

type PipelinesPickerProps = {
  disabled?: boolean;
  placeholder?: string;
  required?: boolean;
  withPortal?: boolean;
  value: PipelinesPicker_ValueFragment | null;
  onChange: (value: PipelinesPicker_ValueFragment | null) => void;
};

const PipelinesPicker = (props: PipelinesPickerProps) => {
  const { t } = useTranslation();
  const {
    value,
    onChange,
    disabled = false,
    required = false,
    withPortal,
    placeholder = t("Select a pipeline"),
  } = props;

  const { data, loading } = useQuery<
    PipelinesPickerQuery,
    PipelinesPickerQueryVariables
  >(
    gql`
      query PipelinesPicker {
        dags {
          items {
            ...PipelinesPicker_value
          }
        }
      }
      ${PipelinesPicker.fragments.value}
    `,
    { fetchPolicy: "cache-first" },
  );
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 150);

  const options = useMemo(() => {
    const lowercaseQuery = debouncedQuery.toLowerCase();
    return (
      data?.dags?.items?.filter((p) =>
        p.externalId.toLowerCase().includes(lowercaseQuery),
      ) ?? []
    );
  }, [data, debouncedQuery]);

  return (
    <Combobox<any>
      required={required}
      onChange={onChange}
      loading={loading}
      withPortal={withPortal}
      displayValue={(value) =>
        value
          ? ensureArray(value)
              .map((v) => v.externalId)
              .join(", ")
          : ""
      }
      by="externalId"
      onInputChange={useCallback((event) => setQuery(event.target.value), [])}
      placeholder={placeholder}
      value={value}
      onClose={useCallback(() => setQuery(""), [])}
      disabled={disabled}
    >
      {options.map((option) => (
        <Combobox.CheckOption key={option.id} value={option}>
          <div className="flex items-center">{option.externalId}</div>
        </Combobox.CheckOption>
      ))}
    </Combobox>
  );
};

PipelinesPicker.fragments = {
  value: gql`
    fragment PipelinesPicker_value on DAG {
      id
      externalId
    }
  `,
};

export default PipelinesPicker;
