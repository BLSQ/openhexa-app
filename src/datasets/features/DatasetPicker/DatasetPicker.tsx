import { gql, useQuery } from "@apollo/client";
import { useCallback, useMemo, useState } from "react";
import { useTranslation } from "next-i18next";
import useDebounce from "core/hooks/useDebounce";
import { Combobox } from "core/components/forms/Combobox";
import { DatasetPickerQuery } from "./DatasetPicker.generated";

type Option = {
  id: string;
  dataset: { slug: string; name: string };
};

type DatasetPickerProps = {
  value?: string;
  workspaceSlug: string;
  placeholder?: string;
  onChange(value?: Option): void;
  required?: boolean;
  disabled?: boolean;
  withPortal?: boolean;
};

const DatasetPicker = (props: DatasetPickerProps) => {
  const { t } = useTranslation();
  const {
    workspaceSlug,
    value,
    disabled = false,
    required = false,
    withPortal = false,
    onChange,
    placeholder = t("Select dataset"),
  } = props;

  const { data, loading } = useQuery<DatasetPickerQuery>(
    gql`
      query DatasetPicker($slug: String!) {
        workspace(slug: $slug) {
          slug
          ...DatasetPicker_workspace
        }
      }
      ${DatasetPicker.fragments.workspace}
    `,
    { variables: { slug: workspaceSlug } },
  );

  const [query, setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 150);

  const options = useMemo(() => {
    const lowercaseQuery = debouncedQuery.toLowerCase();

    return (
      data?.workspace?.datasets.items.filter((item) => {
        return item.dataset.name.toLowerCase().includes(lowercaseQuery);
      }) ?? []
    );
  }, [data, debouncedQuery]);

  const displayValue = useCallback(
    (option: Option) => (option ? option.dataset.name : ""),
    [],
  );

  const comboBoxValue = useMemo(() => {
    return options.find((option) => option.dataset.slug === value) ?? null;
  }, [value, options]);

  return (
    <Combobox
      required={required}
      onChange={onChange}
      loading={loading}
      withPortal={withPortal}
      displayValue={displayValue}
      by={(a, b) => a && b && a.dataset.slug === b.dataset.slug}
      onInputChange={useCallback(
        (event: any) => setQuery(event.target.value),
        [],
      )}
      value={comboBoxValue as any}
      placeholder={placeholder}
      onClose={useCallback(() => setQuery(""), [])}
      disabled={disabled}
    >
      {options.map((option: Option) => (
        <Combobox.CheckOption key={option.id} value={option}>
          {option.dataset.name}
        </Combobox.CheckOption>
      ))}
    </Combobox>
  );
};

DatasetPicker.fragments = {
  workspace: gql`
    fragment DatasetPicker_workspace on Workspace {
      datasets {
        items {
          id
          dataset {
            slug
            name
          }
        }
      }
    }
  `,
};

export default DatasetPicker;
