import { gql, useLazyQuery } from "@apollo/client";
import { useCallback, useEffect, useState } from "react";
import { useTranslation } from "next-i18next";
import { Combobox } from "core/components/forms/Combobox";
import useDebounce from "core/hooks/useDebounce";
import {
  WorkspacePickerQuery,
  WorkspacePickerQueryVariables,
} from "workspaces/features/WorkspacePicker/WorkspacePicker.generated";

type Option = {
  slug: string;
  name: string;
};

type WorkspacePickerProps = {
  value: Option | null;
  placeholder?: string;
  onChange(value: Option | null): void;
  required?: boolean;
  disabled?: boolean;
};

const WorkspacePicker = (props: WorkspacePickerProps) => {
  const { value, ...delegated } = props;
  const { t } = useTranslation();
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 150);
  const [fetch, { data, previousData, loading }] = useLazyQuery<
    WorkspacePickerQuery,
    WorkspacePickerQueryVariables
  >(gql`
    query WorkspacePicker($query: String, $perPage: Int = 10) {
      workspaces(query: $query, page: 1, perPage: $perPage) {
        totalItems
        items {
          ...WorkspacePicker_value
        }
      }
    }
    ${WorkspacePicker.fragments.value}
  `);

  const displayValue = (option: Option) => option?.name ?? "";

  const onOpen = useCallback(() => {
    setQuery("");
  }, []);

  useEffect(() => {
    fetch({ variables: { query: debouncedQuery } });
  }, [fetch, debouncedQuery]);

  const workspaces = (data ?? previousData)?.workspaces ?? {
    items: [],
    totalItems: 0,
  };

  return (
    <Combobox
      {...delegated}
      value={value}
      by="slug"
      loading={loading}
      onOpen={onOpen}
      placeholder={t("Select a workspace")}
      displayValue={displayValue}
      onInputChange={useCallback((event) => setQuery(event.target.value), [])}
      onClose={useCallback(() => setQuery(""), [])}
      withPortal
    >
      {workspaces.items.map((option) => (
        <Combobox.CheckOption value={option} key={option.slug}>
          {displayValue(option)}
        </Combobox.CheckOption>
      ))}
    </Combobox>
  );
};

WorkspacePicker.fragments = {
  value: gql`
    fragment WorkspacePicker_value on Workspace {
      slug
      name
    }
  `,
};

export default WorkspacePicker;
